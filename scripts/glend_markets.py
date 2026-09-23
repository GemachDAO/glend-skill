#!/usr/bin/env python3
"""GLend V2 market health — size, utilisation, withdrawable liquidity, USD. Stdlib only.

GLend V2 only: the Compound V2 deployments on Ethereum and Base. Markets are discovered with
getAllMarkets() and keyed by MARKET ADDRESS (Ethereum has re-registered markets that share
symbols). Every read for a deployment is taken at ONE block, so failing over between RPC
endpoints can never splice two states into one row.

Prints one JSON object per market (NDJSON).

Usage:
    glend_markets.py                        # both deployments
    glend_markets.py --deployment glend-v2-base
"""
from __future__ import annotations

import argparse
import math
import json
import sys
import urllib.request
from datetime import datetime, timezone

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
COMPTROLLER = "0x4a4c2A16b58bD63d37e999fDE50C2eBfE3182D58"  # same address on both chains
DEPLOYMENTS = {
    # cloudflare-eth.com / rpc.ankr.com/eth answer eth_getCode with EMPTY for live contracts;
    # mainnet.base.org rate-limits a per-market loop. None of them are used first.
    "glend-v2-ethereum": (1, "Ethereum", ["https://ethereum-rpc.publicnode.com", "https://eth.drpc.org"], 12.0),
    "glend-v2-base": (8453, "Base", ["https://base-rpc.publicnode.com", "https://mainnet.base.org"], 2.0),
}
# Read ~30s behind head on every chain: 3 blocks on Ethereum, 15 on Base. A fixed block count
# would be ~6s on Base, too close to head for a lagging fallback endpoint to have the block.
CONFIRMATION_SECONDS = 30
SEL = {"getAllMarkets": "0xb0772d0b", "oracle": "0x7dc0d1d0", "symbol": "0x95d89b41",
       "decimals": "0x313ce567", "underlying": "0x6f307dc3", "getCash": "0x3b1d21a2",
       "totalBorrows": "0x47bd3718", "totalReserves": "0x8f840ddd", "totalSupply": "0x18160ddd",
       "exchangeRateStored": "0x182df0f5", "getUnderlyingPrice": "0xfc57d4df"}


def rpc(urls, method, params):
    last = None
    for url in urls:
        req = urllib.request.Request(url, data=json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
            headers={"Content-Type": "application/json", "User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = json.load(r)
        except Exception as exc:
            last = exc
            continue
        err = body.get("error")
        if err:
            if err.get("code") == 3 or "revert" in str(err.get("message", "")).lower():
                return None  # the contract answered: it reverted
            last = RuntimeError(f"{url}: {err.get('message')}")  # e.g. a lagging node: fail over
            continue
        return body.get("result")
    raise RuntimeError(f"{method} failed on every endpoint: {last}")


def call(urls, to, data, block):
    r = rpc(urls, "eth_call", [{"to": to, "data": data}, hex(block)])
    return None if r in (None, "", "0x") else r


def uint(h):
    return None if not h or len(h) < 66 else int(h[2:66], 16)


def addr(h):
    return None if not h or len(h) < 66 else "0x" + h[26:66]


def string(h):
    if not h or len(h) < 130:
        return None
    b = bytes.fromhex(h[2:])
    off = int.from_bytes(b[:32], "big")
    n = int.from_bytes(b[off:off + 32], "big")
    return b[off + 32:off + 32 + n].decode("utf-8", "replace").strip()


def addr_array(h):
    if not h or len(h) < 130:
        return []
    b = h[2:]
    off = int(b[:64], 16) * 2
    n = int(b[off:off + 64], 16)
    return ["0x" + b[off + 64 + i * 64 + 24: off + 64 + (i + 1) * 64] for i in range(n)]


def arg(sel, a):
    return sel + "0" * 24 + a.lower().replace("0x", "")


def ledger_invariant_violated(cash, borrows, reserves, ts, xr) -> bool:
    """Stock Compound V2 defines exchangeRateStored = (cash + borrows - reserves)*1e18 / supply.
    At one block an honest read matches to the wei; a mismatch means a torn read or a changed
    formula. This is a read-consistency check, NOT a solvency signal."""
    return False if ts == 0 else xr != (cash + borrows - reserves) * 10**18 // ts


def read(key, now):
    chain_id, chain_name, urls, block_time = DEPLOYMENTS[key]
    block = int(rpc(urls, "eth_blockNumber", []), 16) - max(1, math.ceil(CONFIRMATION_SECONDS / block_time))
    markets = addr_array(call(urls, COMPTROLLER, SEL["getAllMarkets"], block))
    if not markets:
        raise RuntimeError(f"{key}: getAllMarkets returned nothing")
    oracle = addr(call(urls, COMPTROLLER, SEL["oracle"], block))  # never hardcode the oracle
    out = []
    for m in markets:
        g = lambda s: uint(call(urls, m, SEL[s], block))
        cash, borrows, reserves = g("getCash"), g("totalBorrows"), g("totalReserves") or 0
        ts, xr = g("totalSupply"), g("exchangeRateStored")
        if None in (cash, borrows, ts, xr):
            raise RuntimeError(f"{key}: unreadable market {m}")
        und = addr(call(urls, m, SEL["underlying"], block))  # absent on a native-ETH market
        dec = (uint(call(urls, und, SEL["decimals"], block)) if und else None) or 18
        price = uint(call(urls, oracle, arg(SEL["getUnderlyingPrice"], m), block)) if oracle else None
        if price is None:
            raise RuntimeError(f"{key}: no oracle price for {m}; refusing to emit a row without cash_usd")
        usd = lambda raw: raw * price / 1e36  # price is scaled 1e(36 - decimals)
        supply = cash + borrows - reserves
        rec = {
            "gemach_id": f"{key}-{m.lower()}", "source": "gemach", "feed": "glend_markets",
            "product": "glend", "deployment": key, "chain_id": chain_id, "chain_name": chain_name,
            "market_address": m, "symbol": string(call(urls, m, SEL["symbol"], block)) or "",
            "is_active": supply > 0,
            "utilisation_pct": min(borrows / supply * 100, 100.0) if supply > 0 else 0.0,
            "withdrawable_pct": min(cash / supply * 100, 100.0) if supply > 0 else 0.0,
            "reserves_exceed_cash": reserves > cash,
            "ledger_invariant_violated": ledger_invariant_violated(cash, borrows, reserves, ts, xr),
            "supply_usd": usd(supply), "borrow_usd": usd(borrows), "cash_usd": usd(cash),
            "observed_block": block,
            "upstream_updated_at": int(now.timestamp()), "upstream_updated_source": "chain_read_time",
            "ingestion_date": now.strftime("%Y-%m-%d"),
            "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%S.%f") + "+00:00",
        }
        if und:
            rec["underlying_address"] = und
            rec["underlying_symbol"] = string(call(urls, und, SEL["symbol"], block))
        out.append(rec)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--deployment", choices=sorted(DEPLOYMENTS), nargs="*")
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc)
    for key in (a.deployment or sorted(DEPLOYMENTS)):
        for r in read(key, now):
            sys.stdout.write(json.dumps(r, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

---
name: glend
description: Agent skill for interacting with the Glend DeFi Lend & Borrow protocol by GemachDAO. Supply, borrow, repay, withdraw assets and monitor account health on EVM chains using viem.
---

# Glend Agent Skill

This file provides instructions for AI agents interacting with the **Glend** DeFi Lend & Borrow platform by GemachDAO.

## What is Glend?

Glend is a decentralized lending and borrowing protocol (Aave V3 fork) built on EVM-compatible chains. Agents can:

- **Supply / Lend** — deposit assets to earn interest
- **Borrow** — take loans against supplied collateral
- **Repay** — pay back outstanding debt
- **Withdraw** — reclaim supplied assets (subject to utilization and health factor)
- **Monitor health** — track collateral ratio and liquidation risk

All on-chain interactions are performed with **viem**. Contract addresses and chain configuration are pre-loaded — agents only need a wallet private key to start.

- **Glend App**: `https://glendv2.gemach.io`

---

## Environment Variables

```env
AGENT_PRIVATE_KEY=<private_key>     # Agent wallet private key (never commit!)
```

The only **required** variable is `AGENT_PRIVATE_KEY`. All contract addresses, RPC endpoints, and chain configuration are embedded below.

Optional overrides (advanced — use only if connecting to a custom deployment):

```env
GLEND_RPC_URL=<rpc_url>             # Override the default RPC endpoint
GLEND_POOL_ADDRESS=<address>        # Override the default pool contract
GLEND_CHAIN_ID=<chain_id>           # Override the default chain ID
```

---

## Supported Deployments

### Pharos Testnet (default)

| Property | Value |
|----------|-------|
| **Chain ID** | `688688` |
| **RPC URL** | `https://testnet.dplabs-internal.com` |
| **Block Explorer** | `https://testnet.pharosscan.xyz` |
| **Native Token** | PHRS |
| **Pool (Lending Pool)** | `0xe838eb8011297024bca9c09d4e83e2d3cd74b7d0` |
| **WETHGateway** | `0xa8e550710bf113db6a1b38472118b8d6d5176d12` |
| **Faucet** | `0x2e9d89d372837f71cb529e5ba85bfbc1785c69cd` |

### Token Registry — Pharos Testnet

| Token | Address | Decimals |
|-------|---------|----------|
| USDT | `0x0b00fb1f513e02399667fba50772b21f34c1b5d9` | 6 |
| USDC | `0x48249feeb47a8453023f702f15cf00206eebdf08` | 6 |
| BTC | `0xa4a967fc7cf0e9815bf5c2700a055813628b65be` | 8 |

---

## Getting Test Tokens (Faucet)

Before interacting with the lending pool, agents need test tokens. Use the on-chain faucet to mint tokens:

```typescript
const FAUCET_ABI = [
  {
    name: "mint",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "_asset", type: "address" },
      { name: "_account", type: "address" },
      { name: "_amount", type: "uint256" },
    ],
    outputs: [],
  },
] as const;

const FAUCET_ADDRESS = "0x2e9d89d372837f71cb529e5ba85bfbc1785c69cd" as const;

async function mintTestTokens(
  tokenAddress: `0x${string}`,
  amount: bigint,
) {
  const hash = await walletClient.writeContract({
    address: FAUCET_ADDRESS,
    abi: FAUCET_ABI,
    functionName: "mint",
    args: [tokenAddress, account.address, amount],
  });
  await publicClient.waitForTransactionReceipt({ hash });
  console.log(`Minted test tokens — tx: ${hash}`);
}

// Example: mint 1000 USDC (6 decimals)
await mintTestTokens("0x48249feeb47a8453023f702f15cf00206eebdf08", parseUnits("1000", 6));
```

---

## Core Contract: Glend Lending Pool

All agent operations target the **Glend Pool** contract. Interact with it via `viem`'s `writeContract` / `readContract`.

### Minimal ABI (key functions)

```typescript
export const GLEND_POOL_ABI = [
  // ── Read ──────────────────────────────────────────────────────────────────
  {
    name: "getUserAccountData",
    type: "function",
    stateMutability: "view",
    inputs:  [{ name: "user",  type: "address" }],
    outputs: [
      { name: "totalCollateralBase",     type: "uint256" },
      { name: "totalDebtBase",           type: "uint256" },
      { name: "availableBorrowsBase",    type: "uint256" },
      { name: "currentLiquidationThreshold", type: "uint256" },
      { name: "ltv",                     type: "uint256" },
      { name: "healthFactor",            type: "uint256" },
    ],
  },
  {
    name: "getReserveData",
    type: "function",
    stateMutability: "view",
    inputs:  [{ name: "asset", type: "address" }],
    outputs: [
      { name: "configuration",    type: "uint256" },
      { name: "liquidityIndex",   type: "uint128" },
      { name: "variableBorrowIndex", type: "uint128" },
      { name: "currentLiquidityRate",      type: "uint128" },
      { name: "currentVariableBorrowRate", type: "uint128" },
      { name: "lastUpdateTimestamp",       type: "uint40"  },
      { name: "aTokenAddress",             type: "address" },
      { name: "variableDebtTokenAddress",  type: "address" },
      { name: "interestRateStrategyAddress", type: "address" },
      { name: "id",               type: "uint8"   },
    ],
  },
  // ── Write ─────────────────────────────────────────────────────────────────
  {
    name: "supply",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "asset",          type: "address" },
      { name: "amount",         type: "uint256" },
      { name: "onBehalfOf",     type: "address" },
      { name: "referralCode",   type: "uint16"  },
    ],
    outputs: [],
  },
  {
    name: "withdraw",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "asset",      type: "address" },
      { name: "amount",     type: "uint256" },   // use MaxUint256 to withdraw all
      { name: "to",         type: "address" },
    ],
    outputs: [{ name: "", type: "uint256" }],
  },
  {
    name: "borrow",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "asset",              type: "address" },
      { name: "amount",             type: "uint256" },
      { name: "interestRateMode",   type: "uint256" }, // 2 = variable
      { name: "referralCode",       type: "uint16"  },
      { name: "onBehalfOf",         type: "address" },
    ],
    outputs: [],
  },
  {
    name: "repay",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "asset",            type: "address" },
      { name: "amount",           type: "uint256" }, // use MaxUint256 to repay all
      { name: "interestRateMode", type: "uint256" }, // 2 = variable
      { name: "onBehalfOf",       type: "address" },
    ],
    outputs: [{ name: "", type: "uint256" }],
  },
] as const;
```

---

## Agent Operations

### 1 · Set up viem clients

```typescript
import {
  createPublicClient,
  createWalletClient,
  http,
  parseUnits,
  formatUnits,
  maxUint256,
  defineChain,
} from "viem";
import { privateKeyToAccount } from "viem/accounts";
import type { Chain } from "viem";

// ── Pre-configured Glend deployment on Pharos Testnet ──────────────────────
const pharosTestnet = defineChain({
  id: 688688,
  name: "Pharos Testnet",
  nativeCurrency: { name: "PHRS", symbol: "PHRS", decimals: 18 },
  rpcUrls: {
    default: { http: ["https://testnet.dplabs-internal.com"] },
  },
  blockExplorers: {
    default: { name: "Pharos Explorer", url: "https://testnet.pharosscan.xyz" },
  },
  testnet: true,
});

// ── Contract addresses (Pharos Testnet defaults) ───────────────────────────
const GLEND_DEPLOYMENTS = {
  688688: {
    chain: pharosTestnet,
    pool: "0xe838eb8011297024bca9c09d4e83e2d3cd74b7d0" as `0x${string}`,
    wethGateway: "0xa8e550710bf113db6a1b38472118b8d6d5176d12" as `0x${string}`,
    faucet: "0x2e9d89d372837f71cb529e5ba85bfbc1785c69cd" as `0x${string}`,
    tokens: {
      USDT:  { address: "0x0b00fb1f513e02399667fba50772b21f34c1b5d9" as `0x${string}`, decimals: 6 },
      USDC:  { address: "0x48249feeb47a8453023f702f15cf00206eebdf08" as `0x${string}`, decimals: 6 },
      BTC:   { address: "0xa4a967fc7cf0e9815bf5c2700a055813628b65be" as `0x${string}`, decimals: 8 },
    },
  },
} as const;

// ── Resolve configuration (env overrides or Pharos Testnet defaults) ───────
const CHAIN_ID      = Number(process.env.GLEND_CHAIN_ID ?? 688688);
const deployment    = GLEND_DEPLOYMENTS[CHAIN_ID as keyof typeof GLEND_DEPLOYMENTS];
if (!deployment) {
  throw new Error(`Unsupported chain ID: ${CHAIN_ID}. Supported: ${Object.keys(GLEND_DEPLOYMENTS).join(", ")}`);
}
const chain: Chain  = deployment.chain;
const POOL_ADDRESS  = (process.env.GLEND_POOL_ADDRESS ?? deployment.pool) as `0x${string}`;
const RPC_URL       = process.env.GLEND_RPC_URL ?? chain.rpcUrls.default.http[0];
const PRIVATE_KEY   = process.env.AGENT_PRIVATE_KEY as `0x${string}`;

const account       = privateKeyToAccount(PRIVATE_KEY);
const publicClient  = createPublicClient({ chain, transport: http(RPC_URL) });
const walletClient  = createWalletClient({ account, chain, transport: http(RPC_URL) });

// ── Helper: look up a token by symbol ──────────────────────────────────────
function getToken(symbol: string) {
  const tokens = deployment?.tokens;
  if (!tokens) throw new Error(`No token registry for chain ${CHAIN_ID}. Supported chains: ${Object.keys(GLEND_DEPLOYMENTS).join(", ")}`);
  const token = tokens[symbol as keyof typeof tokens];
  if (!token) throw new Error(`Unknown token: ${symbol}. Available: ${Object.keys(tokens).join(", ")}`);
  return token;
}
```

### 2 · Approve ERC-20 before supply or repay

```typescript
import { erc20Abi } from "viem";

async function approveToken(tokenAddress: `0x${string}`, amount: bigint) {
  const hash = await walletClient.writeContract({
    address: tokenAddress,
    abi: erc20Abi,
    functionName: "approve",
    args: [POOL_ADDRESS, amount],
  });
  await publicClient.waitForTransactionReceipt({ hash });
  console.log("Approved:", hash);
}
```

### 3 · Supply (lend) assets

```typescript
async function supplyAsset(
  tokenAddress: `0x${string}`,
  humanAmount: string,
  decimals: number,
) {
  const amount = parseUnits(humanAmount, decimals);
  await approveToken(tokenAddress, amount);

  const hash = await walletClient.writeContract({
    address: POOL_ADDRESS,
    abi: GLEND_POOL_ABI,
    functionName: "supply",
    args: [tokenAddress, amount, account.address, 0],
  });
  await publicClient.waitForTransactionReceipt({ hash });
  console.log(`Supplied ${humanAmount} — tx: ${hash}`);
}
```

### 4 · Borrow assets

```typescript
async function borrowAsset(
  tokenAddress: `0x${string}`,
  humanAmount: string,
  decimals: number,
) {
  const amount = parseUnits(humanAmount, decimals);
  const hash = await walletClient.writeContract({
    address: POOL_ADDRESS,
    abi: GLEND_POOL_ABI,
    functionName: "borrow",
    args: [tokenAddress, amount, 2n, 0, account.address], // 2 = variable rate
  });
  await publicClient.waitForTransactionReceipt({ hash });
  console.log(`Borrowed ${humanAmount} — tx: ${hash}`);
}
```

### 5 · Repay debt

```typescript
import { erc20Abi } from "viem";

/** Fetch the current variable debt balance for a token. */
async function getDebtBalance(
  variableDebtTokenAddress: `0x${string}`,
  userAddress: `0x${string}`,
): Promise<bigint> {
  return publicClient.readContract({
    address: variableDebtTokenAddress,
    abi: erc20Abi,
    functionName: "balanceOf",
    args: [userAddress],
  });
}

async function repayDebt(
  tokenAddress: `0x${string}`,
  variableDebtTokenAddress: `0x${string}`,
  humanAmount: string | "all",
  decimals: number,
) {
  // Determine the repay amount for the Pool call (maxUint256 = repay all debt)
  const repayAmount = humanAmount === "all" ? maxUint256 : parseUnits(humanAmount, decimals);

  // For the ERC-20 approval, always approve the exact token amount being transferred.
  // When repaying "all", query the live debt balance so the approval is not excessive.
  const approvalAmount =
    humanAmount === "all"
      ? await getDebtBalance(variableDebtTokenAddress, account.address)
      : parseUnits(humanAmount, decimals);

  await approveToken(tokenAddress, approvalAmount);

  const hash = await walletClient.writeContract({
    address: POOL_ADDRESS,
    abi: GLEND_POOL_ABI,
    functionName: "repay",
    args: [tokenAddress, repayAmount, 2n, account.address],
  });
  await publicClient.waitForTransactionReceipt({ hash });
  console.log(`Repaid — tx: ${hash}`);
}
```

### 6 · Withdraw supplied assets

```typescript
async function withdrawAsset(
  tokenAddress: `0x${string}`,
  humanAmount: string | "all",
  decimals: number,
) {
  const amount = humanAmount === "all" ? maxUint256 : parseUnits(humanAmount, decimals);

  const hash = await walletClient.writeContract({
    address: POOL_ADDRESS,
    abi: GLEND_POOL_ABI,
    functionName: "withdraw",
    args: [tokenAddress, amount, account.address],
  });
  await publicClient.waitForTransactionReceipt({ hash });
  console.log(`Withdrew — tx: ${hash}`);
}
```

### 7 · Check account health

```typescript
async function getAccountHealth(userAddress: `0x${string}`) {
  const data = await publicClient.readContract({
    address: POOL_ADDRESS,
    abi: GLEND_POOL_ABI,
    functionName: "getUserAccountData",
    args: [userAddress],
  });

  const [
    totalCollateralBase,
    totalDebtBase,
    availableBorrowsBase,
    currentLiquidationThreshold,
    ltv,
    healthFactor,
  ] = data;

  // healthFactor is scaled by 1e18 — values below 1e18 risk liquidation
  const hf = formatUnits(healthFactor, 18);
  console.log({
    totalCollateral: formatUnits(totalCollateralBase, 8),
    totalDebt:       formatUnits(totalDebtBase, 8),
    availableToBorrow: formatUnits(availableBorrowsBase, 8),
    healthFactor: hf,
    atRisk: Number(hf) < 1.1,
  });

  return { totalCollateralBase, totalDebtBase, availableBorrowsBase, healthFactor };
}
```

### 8 · Get reserve (market) data

```typescript
async function getMarketData(tokenAddress: `0x${string}`) {
  const data = await publicClient.readContract({
    address: POOL_ADDRESS,
    abi: GLEND_POOL_ABI,
    functionName: "getReserveData",
    args: [tokenAddress],
  });

  // Rates are per-second values in ray units (1e27).
  // Annualise using compound-interest: APY = (1 + ratePerSecond)^31_536_000 - 1
  const SECONDS_PER_YEAR = 31_536_000n;
  const RAY = 10n ** 27n;

  function rayToAPY(rayRate: bigint): string {
    // Use floating-point for the exponentiation
    const ratePerSecond = Number(rayRate) / Number(RAY);
    const apy = (Math.pow(1 + ratePerSecond, Number(SECONDS_PER_YEAR)) - 1) * 100;
    return `${apy.toFixed(2)}%`;
  }

  const supplyAPY = rayToAPY(data.currentLiquidityRate);
  const borrowAPY = rayToAPY(data.currentVariableBorrowRate);

  console.log({ supplyAPY, borrowAPY });
  return data;
}
```

---

## Key Safety Rules for Agents

1. **Always check health factor before borrowing** — keep it above **1.5** to avoid liquidation risk.
2. **Approve the exact amount** before `supply` and `repay`; never set an open-ended allowance. When repaying "all" debt, query the live debt balance first and approve only that amount.
3. **`maxUint256` is for the Pool call, not for approvals** — passing `maxUint256` to `repay()` tells the contract to repay all debt; the ERC-20 approval must still use the precise token amount.
4. **Simulate transactions** with `publicClient.simulateContract` before sending:

```typescript
const { request } = await publicClient.simulateContract({
  address: POOL_ADDRESS,
  abi: GLEND_POOL_ABI,
  functionName: "borrow",
  args: [tokenAddress, amount, 2n, 0, account.address],
  account,
});
const hash = await walletClient.writeContract(request);
```

5. **Wait for receipt** before assuming a transaction succeeded.
6. **Never log or commit private keys**; read them from environment variables only.

---

## Typical Agent Workflow

```
1. mintTestTokens(getToken("USDC").address, parseUnits("1000", 6))
   → get test USDC from faucet

2. getAccountHealth(agentAddress)
   → confirm healthFactor > 1.5 before borrowing

3. supplyAsset(getToken("USDC").address, "1000", 6)
   → deposit 1000 USDC as collateral

4. getAccountHealth(agentAddress)
   → verify collateral registered, check availableBorrowsBase

5. borrowAsset(getToken("USDT").address, "500", 6)
   → borrow 500 USDT against USDC collateral

6. [... use borrowed funds ...]

7. repayDebt(getToken("USDT").address, variableDebtTokenAddress, "all", 6)
   → repay full USDT debt

8. withdrawAsset(getToken("USDC").address, "all", 6)
   → recover USDC collateral
```

---

## Troubleshooting

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `CALLER_NOT_IN_WHITELIST` | Protocol access control | Confirm the agent wallet is allowed |
| `HEALTH_FACTOR_LOWER_THAN_LIQUIDATION_THRESHOLD` | Borrow would make account unsafe | Reduce borrow amount |
| `NO_ACTIVE_RESERVE` | Wrong token address or chain | Use addresses from the Token Registry above |
| `TRANSFER_AMOUNT_EXCEEDS_BALANCE` | Insufficient token balance | Use the faucet to mint test tokens |
| ERC-20 allowance error | `approve()` not called first | Call `approveToken()` before supply/repay |

---

## Resources

- Glend App: `https://glendv2.gemach.io`
- Pharos Testnet Explorer: `https://testnet.pharosscan.xyz`
- GemachDAO: `https://github.com/GemachDAO`
- viem docs: `https://viem.sh`

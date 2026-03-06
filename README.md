# Glend-Skill

```
   ██████╗ ██╗     ███████╗███╗   ██╗██████╗
  ██╔════╝ ██║     ██╔════╝████╗  ██║██╔══██╗
  ██║  ███╗██║     █████╗  ██╔██╗ ██║██║  ██║
  ██║   ██║██║     ██╔══╝  ██║╚██╗██║██║  ██║
  ╚██████╔╝███████╗███████╗██║ ╚████║██████╔╝
   ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═══╝╚═════╝
        ⚡ Powered by Gemach ⚡
    DeFi Lend & Borrow — Agent Skill
```

Glend-Skill is an AI agent skill that enables agents to interact with the **Glend** DeFi Lend & Borrow platform by GemachDAO. It adheres to the [skills.sh](https://skills.sh) specification.

## Overview

Glend is a decentralized lending and borrowing protocol on EVM-compatible chains. Once this skill is installed, an agent can autonomously:

- **Supply / Lend** assets to earn interest
- **Borrow** against supplied collateral
- **Repay** outstanding debt
- **Withdraw** collateral
- **Monitor** account health factor and liquidation risk

## Installation

```bash
npx skills add GemachDAO/glend-skill
```

```
   ██████╗ ██╗     ███████╗███╗   ██╗██████╗
  ██╔════╝ ██║     ██╔════╝████╗  ██║██╔══██╗
  ██║  ███╗██║     █████╗  ██╔██╗ ██║██║  ██║
  ██║   ██║██║     ██╔══╝  ██║╚██╗██║██║  ██║
  ╚██████╔╝███████╗███████╗██║ ╚████║██████╔╝
   ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═══╝╚═════╝
        ⚡ Powered by Gemach ⚡
    DeFi Lend & Borrow — Agent Skill

  ✅ Skill installed — ready to lend & borrow!
```

## How it works

This repository is a self-contained agent protocol instruction set — everything an agent needs is right here:

- **`SKILL.md`** — core agent instructions: pre-configured contracts, viem setup, ABI, typed code examples for every lending operation, safety rules, and a typical workflow.
- **`package.json`** — metadata conforming to the skills.sh standard.

No external repositories or private dependencies are required. All contract addresses, chain configuration, and token registries are embedded in `SKILL.md`.

## What agents can do

| Action | Description |
|--------|-------------|
| `mintTestTokens` | Get test tokens from the on-chain faucet (Pharos) |
| `supplyAsset` | Deposit ERC-20 tokens to earn lending APY (Aave V3) |
| `borrowAsset` | Borrow tokens against existing collateral (Aave V3) |
| `repayDebt` | Repay variable-rate debt (Aave V3) |
| `withdrawAsset` | Reclaim supplied tokens (Aave V3) |
| `compoundSupply` | Supply tokens to a gToken market (Compound) |
| `compoundBorrow` | Borrow against collateral (Compound) |
| `compoundRepay` | Repay debt (Compound) |
| `compoundWithdraw` | Redeem gTokens for underlying (Compound) |
| `enableCollateral` | Enable gToken markets as collateral (Compound) |
| `getAccountHealth` | Check health factor and borrow capacity (Aave V3) |
| `getCompoundAccountHealth` | Check liquidity and shortfall (Compound) |
| `getMarketData` | Fetch supply/borrow APYs (Aave V3) |
| `getCompoundMarketRates` | Fetch supply/borrow APYs (Compound) |

## Pre-configured Deployments

Agents work out of the box on all supported chains with zero configuration:

### Pharos Testnet — Aave V3 (default)

| Property | Value |
|----------|-------|
| **Chain ID** | `688688` |
| **Pool** | `0xe838eb8011297024bca9c09d4e83e2d3cd74b7d0` |
| **RPC** | `https://testnet.dplabs-internal.com` |
| **Explorer** | [testnet.pharosscan.xyz](https://testnet.pharosscan.xyz) |
| **Tokens** | USDT, USDC, BTC |

### Ethereum Mainnet — Compound fork

| Property | Value |
|----------|-------|
| **Chain ID** | `1` |
| **Comptroller** | `0x4a4c2A16b58bD63d37e999fDE50C2eBfE3182D58` |
| **Markets** | tUSDT, tUSDC, tETH, tcbBTC, tstETH |
| **Explorer** | [etherscan.io](https://etherscan.io) |

### Base — Compound fork

| Property | Value |
|----------|-------|
| **Chain ID** | `8453` |
| **Comptroller** | `0x4a4c2A16b58bD63d37e999fDE50C2eBfE3182D58` |
| **Markets** | gUSDT, gUSDC, gETH, gcbBTC |
| **Explorer** | [basescan.org](https://basescan.org) |

## Required Environment Variables

```env
AGENT_PRIVATE_KEY=<private_key>     # Agent wallet private key (never commit!)
```

That's it! All other configuration (RPC, contracts, chain) is pre-loaded.

## Compatibility

Compatible with all [skills.sh](https://skills.sh) agent frameworks including Claude Code, Cursor, Copilot, Windsurf, OpenCode, and more.

## Resources

- Glend App: [glendv2.gemach.io](https://glendv2.gemach.io)
- Pharos Explorer: [testnet.pharosscan.xyz](https://testnet.pharosscan.xyz)
- Ethereum Explorer: [etherscan.io](https://etherscan.io)
- Base Explorer: [basescan.org](https://basescan.org)
- GemachDAO: [github.com/GemachDAO](https://github.com/GemachDAO)
- viem docs: [viem.sh](https://viem.sh)
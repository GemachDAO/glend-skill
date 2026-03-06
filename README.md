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
| `mintTestTokens` | Get test tokens from the on-chain faucet |
| `supplyAsset` | Deposit ERC-20 tokens to earn lending APY |
| `borrowAsset` | Borrow tokens against existing collateral |
| `repayDebt` | Repay variable-rate debt (partial or full) |
| `withdrawAsset` | Reclaim supplied tokens |
| `getAccountHealth` | Check health factor, collateral, and borrow capacity |
| `getMarketData` | Fetch current supply/borrow APYs for any reserve |

## Pre-configured Deployment — Pharos Testnet

Agents work out of the box on **Pharos Testnet** with zero configuration:

| Property | Value |
|----------|-------|
| **Chain ID** | `688688` |
| **Pool** | `0xe838eb8011297024bca9c09d4e83e2d3cd74b7d0` |
| **RPC** | `https://testnet.dplabs-internal.com` |
| **Explorer** | [testnet.pharosscan.xyz](https://testnet.pharosscan.xyz) |
| **Tokens** | USDT, USDC, BTC |

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
- GemachDAO: [github.com/GemachDAO](https://github.com/GemachDAO)
- viem docs: [viem.sh](https://viem.sh)
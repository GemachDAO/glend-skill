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

## How it works

This repository is a self-contained agent protocol instruction set — everything an agent needs is right here:

- **`SKILL.md`** — core agent instructions: viem setup, contract ABI, typed code examples for every lending operation, safety rules, and a typical workflow.
- **`package.json`** — metadata conforming to the skills.sh standard.

No external repositories or private dependencies are required.

## What agents can do

| Action | Description |
|--------|-------------|
| `supplyAsset` | Deposit ERC-20 tokens to earn lending APY |
| `borrowAsset` | Borrow tokens against existing collateral |
| `repayDebt` | Repay variable-rate debt (partial or full) |
| `withdrawAsset` | Reclaim supplied tokens |
| `getAccountHealth` | Check health factor, collateral, and borrow capacity |
| `getMarketData` | Fetch current supply/borrow APYs for any reserve |

## Required Environment Variables

```env
GLEND_CHAIN_ID=<chain_id>           # e.g. 1 for Ethereum mainnet
GLEND_POOL_ADDRESS=<address>        # Glend lending pool contract
GLEND_RPC_URL=<rpc_url>             # EVM JSON-RPC endpoint
AGENT_PRIVATE_KEY=<private_key>     # Agent wallet private key (never commit!)
```

## Compatibility

Compatible with all [skills.sh](https://skills.sh) agent frameworks including Claude Code, Cursor, Copilot, Windsurf, OpenCode, and more.

## Resources

- GemachDAO: [github.com/GemachDAO](https://github.com/GemachDAO)
- viem docs: [viem.sh](https://viem.sh)
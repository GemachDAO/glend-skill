# Glend-Skill

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

This repository is an agent protocol instruction set:

- **`SKILL.md`** — core agent instructions: viem setup, contract ABI, typed code examples for every lending operation, safety rules, and a typical workflow.
- **`package.json`** — metadata conforming to the skills.sh standard.

## What agents can do

| Action | Description |
|--------|-------------|
| `supplyAsset` | Deposit ERC-20 tokens to earn lending APY |
| `borrowAsset` | Borrow tokens against existing collateral |
| `repayDebt` | Repay variable-rate debt (partial or full) |
| `withdrawAsset` | Reclaim supplied tokens |
| `getAccountHealth` | Check health factor, collateral, and borrow capacity |
| `getMarketData` | Fetch current supply/borrow APYs for any reserve |

## Glend Frontend Stack

- React / Next.js (App Router)
- Tailwind CSS
- NextUI
- Zustand (state management)
- viem (on-chain interaction)
- TypeScript
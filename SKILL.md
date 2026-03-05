# Glend Agent Skill

This file provides instructions for AI agents interacting with the **Glend** DeFi Lend & Borrow platform by GemachDAO.

## What is Glend?

Glend is a decentralized lending and borrowing protocol built on EVM-compatible chains. Users (and agents) can:

- **Supply / Lend** — deposit assets to earn interest
- **Borrow** — take loans against supplied collateral
- **Repay** — pay back outstanding debt
- **Withdraw** — reclaim supplied assets (subject to utilization and health factor)
- **Monitor health** — track collateral ratio and liquidation risk

The frontend is a **Next.js / React** application (Tailwind CSS, NextUI, Zustand state management) and all on-chain interactions are performed with **viem**.

---

## Quick Setup

```bash
# Clone the frontend and install dependencies
git clone https://github.com/GemachDAO/Glend-Front-End
cd Glend-Front-End
npm install

# Copy and fill environment variables
cp .env.example .env.local
```

### Required environment variables

```env
NEXT_PUBLIC_CHAIN_ID=<chain_id>           # e.g. 1 for Ethereum mainnet
NEXT_PUBLIC_GLEND_POOL_ADDRESS=<address>  # Glend lending pool contract
NEXT_PUBLIC_RPC_URL=<rpc_url>             # EVM JSON-RPC endpoint
```

### Development server

```bash
npm run dev     # starts Next.js on http://localhost:3000
npm run build   # production build
npm run start   # serve production build
npm run lint    # ESLint check
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js (App Router) |
| UI | React 18, Tailwind CSS, NextUI |
| State | Zustand |
| On-chain | viem |
| Language | TypeScript |

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
} from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { mainnet, sepolia, arbitrum, base, optimism } from "viem/chains";
import type { Chain } from "viem";

const POOL_ADDRESS  = process.env.NEXT_PUBLIC_GLEND_POOL_ADDRESS as `0x${string}`;
const RPC_URL       = process.env.NEXT_PUBLIC_RPC_URL!;
const PRIVATE_KEY   = process.env.AGENT_PRIVATE_KEY as `0x${string}`;
const CHAIN_ID      = Number(process.env.NEXT_PUBLIC_CHAIN_ID ?? mainnet.id);

// Map well-known chain IDs to viem chain objects; extend as Glend deploys to new networks
const SUPPORTED_CHAINS: Record<number, Chain> = {
  [mainnet.id]:   mainnet,
  [sepolia.id]:   sepolia,
  [arbitrum.id]:  arbitrum,
  [base.id]:      base,
  [optimism.id]:  optimism,
};
const chain: Chain = SUPPORTED_CHAINS[CHAIN_ID] ?? mainnet;

const account = privateKeyToAccount(PRIVATE_KEY);

const publicClient = createPublicClient({ chain, transport: http(RPC_URL) });
const walletClient = createWalletClient({ account, chain, transport: http(RPC_URL) });
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

## Zustand Store (Frontend State)

The frontend manages connection state via a Zustand store in `store/useGlendStore.ts`. When building on top of the frontend code, use these selectors:

```typescript
import { useGlendStore } from "@/store/useGlendStore";

const { address, supplies, borrows, healthFactor, isConnected } = useGlendStore();
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
1. getAccountHealth(agentAddress)
   → confirm healthFactor > 1.5 before borrowing

2. supplyAsset(USDC_ADDRESS, "1000", 6)
   → deposit 1000 USDC as collateral

3. getAccountHealth(agentAddress)
   → verify collateral registered, check availableBorrowsBase

4. borrowAsset(WETH_ADDRESS, "0.3", 18)
   → borrow 0.3 WETH against USDC collateral

5. [... use borrowed funds ...]

6. repayDebt(WETH_ADDRESS, "all", 18)
   → repay full WETH debt

7. withdrawAsset(USDC_ADDRESS, "all", 6)
   → recover USDC collateral
```

---

## Troubleshooting

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `CALLER_NOT_IN_WHITELIST` | Protocol access control | Confirm the agent wallet is allowed |
| `HEALTH_FACTOR_LOWER_THAN_LIQUIDATION_THRESHOLD` | Borrow would make account unsafe | Reduce borrow amount |
| `NO_ACTIVE_RESERVE` | Wrong token address or chain | Double-check `NEXT_PUBLIC_CHAIN_ID` and token address |
| `TRANSFER_AMOUNT_EXCEEDS_BALANCE` | Insufficient token balance | Fund the agent wallet |
| ERC-20 allowance error | `approve()` not called first | Call `approveToken()` before supply/repay |

---

## Resources

- Glend Frontend: `https://github.com/GemachDAO/Glend-Front-End`
- GemachDAO: `https://github.com/GemachDAO`
- viem docs: `https://viem.sh`
- NextUI docs: `https://nextui.org`

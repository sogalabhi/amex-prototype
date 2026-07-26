# Verdict Chain — Ledger & Trust Architecture Guide

This document explains **Verdict Chain's** trust model, including the **live EVM devnet cryptographic commitments** implemented in the Round 1 submission and the **Paladin Pente multi-party privacy roadmap** for production.

---

## 1. Prototype Architecture: EVM Devnet Commitments (Implemented Today)

In the current prototype build:
1. **Off-Chain Adjudication:** Raw evidence documents, customer claims, chat transcripts, and rule evaluations are processed off-chain.
2. **SHA-256 Verdict Commitment:** When a resolution completes, the system computes `SHA-256(verdict + raw_score + confidence + fired_rules)`.
3. **On-Chain Anchoring:** The backend executes JSON-RPC (`eth_sendTransaction`) to store the commitment hash directly into the calldata of a live EVM node (Anvil running in Docker on port `8545`).
4. **Immutability & Non-Repudiation:** No raw claim data or PII is written to the chain — only the preimage-resistant hash commitment. Neither party can alter evidence or rule scores after the fact without invalidating the on-chain hash.

---

## 2. Target Production Architecture: Paladin Pente Privacy Groups (Roadmap)

In enterprise cardmember dispute resolution (e.g. American Express), broadcasting transaction hashes on a public EVM node is insufficient due to customer privacy regulations (GDPR, PCI-DSS, banking secrecy).

**Paladin** (hosted under Linux Foundation Decentralized Trust) is an open-source framework for **programmable privacy**:

- **Pente Protocol:** Creates 3-party private execution groups between **Cardmember (Issuer Portal)**, **Merchant**, and **Issuer (Amex Ops)**.
- **Confidential Smart Contracts:** Contract state and evidence remain 100% confidential off-chain between the three authorized parties.
- **Zero-Knowledge Commitments:** Paladin automatically publishes cryptographic state commitments to the underlying shared ledger.

---

## 3. Terminal Verification Commands

You can verify that commitment transactions are actively being mined on the local EVM container using standard JSON-RPC `curl` commands.

### Query Latest Block Number:
```bash
curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' | python3 -m json.tool
```

### Inspect Mined Commitment Transaction:
```bash
curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":["<YOUR_TX_HASH_HERE>"],"id":1}' | python3 -m json.tool
```

### Query Execution Receipt:
```bash
curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getTransactionReceipt","params":["<YOUR_TX_HASH_HERE>"],"id":1}' | python3 -m json.tool
```

---

## 4. Pitch & Video Framing

> **"Every verdict is sealed with a cryptographic hash commitment and written to an EVM ledger — no dispute data ever goes on-chain, only the commitment, so neither party can alter the evidence set or the reasoning after the fact, and both can verify the decision trail independently. In production, each dispute runs inside a Paladin Pente privacy group shared by cardmember, merchant, and issuer, so the evidence itself is confidential to those three parties while the outcome stays provable on the shared ledger."**

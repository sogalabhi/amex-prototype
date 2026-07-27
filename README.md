# Verdict Chain — AI-Powered Chargeback Adjudication & Trust Ledger

> **American Express Hackathon — Round 1 Submission & Production Roadmap**  
> *Frictionless Dispute & Chargeback Resolution*  
> *Independent student project, not affiliated with American Express*

<img width="2790" height="1408" alt="image" src="https://github.com/user-attachments/assets/23f8b619-e484-4812-9210-b98ef6f4889a" />

<img width="350" height="900" alt="image" src="https://github.com/user-attachments/assets/29f2eca6-b760-43d1-a70b-577821e91af3" />

<img width="2880" height="1554" alt="image" src="https://github.com/user-attachments/assets/4409095e-d17b-4cba-84f9-fc20d2f33af8" />

## 📌 Executive Overview

Credit card chargeback adjudication is historically slow (30–90 days), labor-intensive ($9.08–$10.32 per dispute in issuer ops costs), and opaque to both Cardmembers and Merchants.

**Verdict Chain** solves this by strictly decoupling **AI Perception** from **Deterministic Rule Adjudication**:

> **"The AI never decides anything. It only reads. American Express's published rulebook decides — and the ledger proves nobody changed the answer."**

1. **AI Perception Layer:** Parses unstructured evidence (PDF receipts, courier tracking scans, customer chat logs) into atomic facts carrying source provenance.
2. **Deterministic Rules Engine:** Hardcoded Python engine evaluating published Amex chargeback reason codes, enforcing defeater logic and procedural exclusions.
3. **Audit & Trust Ledger:** Cryptographically anchors a SHA-256 state hash of every pipeline step on-chain for tamper-evident verifiability.

---

## 🛠️ What is Built & Working Today (Round 1 Working Prototype)

The current repository contains a fully operational end-to-end prototype comprising a FastAPI backend, OpenRouter LLM pipeline (`openai/gpt-4o-mini`), Python rules engine, live EVM blockchain commitment engine, and a React SPA frontend.

### 1. The 6-Stage Operational Pipeline
- **Stage 1: Classification (AI):** Classifies raw claims into Amex Reason Codes (4554, 4553, 4512, 4544).
- **Stage 2: Atomic Fact Extraction (AI):** Extracts observable facts from evidence documents with source provenance.
- **Stage 3: Cross-Document Derivation (Python):** Computes normalized address mismatches, distinct ticket numbers, and signature verification.
- **Stage 4: Deterministic Scoring Engine (Python):** 
  - **Exclusion Gate:** Checks procedural exclusions prior to scoring (e.g., Code 4512 airline ticket exclusions).
  - **Defeater Engine:** Suppresses invalidated merchant defenses (e.g. wrong delivery address suppresses POD defense `4554-D2` to `0.00` weight).
  - **Normalized Confidence:** $\text{Confidence} = \frac{|\text{Raw Score}|}{\sum |\text{All Applicable Weights Including Defeated}|}$
- **Stage 5: Dual Decision Memos (AI):** Generates Cardmember and Merchant decision memos citing exact fact IDs and verbatim rulebook text.
- **Stage 6: Blockchain Commitment (EVM RPC):** Mines SHA-256 state hashes directly to an EVM devnet ledger via `eth_sendTransaction` (Anvil RPC port 8545).

### 2. Verified Benchmark Matrix (100% Ground Truth Agreement)

| Case ID | Reason Code | Scenario Narrative | Expected Outcome | Verified Prototype Result | Measured Time | Confidence | Key Rule Mechanics Fired |
|---|---|---|---|---|---|---|---|
| **CASE A** | 4554 | Electronics order; courier delivered parcel to #41 Marlowe St instead of order shipping address #14 Marlowe St. | **CARDMEMBER WINS** | **CARDMEMBER** | 20.4s | **60.0%** | `4554-D2` (−0.90) **DEFEATED** by address mismatch; `4554-C2` & `C3` active. |
| **CASE B** | 4554 | Camping gear order; merchant submits signed POD to exact address plus chat log where customer acknowledges receipt. | **MERCHANT WINS** | **MERCHANT** | 17.8s | **100.0%** | `4554-D1`, `D2`, `D5` all active. 100% evidence balance. |
| **CASE C** | 4553 | Dining chairs with visible backrest seam; merchant cites timber variation policy; cardmember insists seam is physical defect. | **ESCALATE TO HUMAN** | **ESCALATE_HUMAN_REVIEW** | 23.6s | **17.8%** | `4553-D1` & `D5` **DEFEATED** by defect claim. Raw score +0.65, conf 17.8% < 50% cutoff $\rightarrow$ escalate. |
| **CASE D** | 4512 | Two identical charges of $1,890.00 40 mins apart for flight bookings. Cardmember claims duplicate; merchant proves separate flown tickets. | **PROCEDURAL EXCLUSION** | **NOT_CHARGEABLE_UNDER_CODE** | 27.3s | **100.0%** | Exclusion `4512-X1` triggered by distinct ticket numbers (`distinct_ticket_numbers`). Short-circuits scoring. |

*Demonstrated Resolution Latency: **17–27 seconds** across all four distinct outcome types.*

---

## 🚀 Finale Roadmap: What We Will Build for the Hackathon Finale

Our target features for the Aug 7–21 Finale Round expand the prototype into an enterprise-grade platform:

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 HACKATHON FINALE PRODUCTION VISION                                   │
│                                                                                                       │
│  ┌───────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────────────┐  │
│  │ 0. Stage 0 Triage     │      │ 1. Paladin Pente        │      │ 2. Multi-Tenant Portals         │  │
│  │    (Merchant Remedy)  │      │    3-Party Privacy Group│      │    Cardmember, Merchant, Ops    │  │
│  └───────────────────────┘      └─────────────────────────┘      └─────────────────────────────────┘  │
│                                                                                                       │
│  ┌───────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────────────┐  │
│  │ 3. Agentic Evidence   │      │ 4. Full 24 Amex Reason  │      │ 5. 50-Case Quantitative         │  │
│  │    Connectors         │      │    Code Matrix          │      │    Fairness Evaluation Suite    │  │
│  └───────────────────────┘      └─────────────────────────┘      └─────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Stage 0 Pre-Dispute Triage:** Automatically intercepts friendly fraud prior to formal chargeback scoring, checking if the merchant already offers an active remedy (return window, store credit, exchange) to save $9–$10 issuer fees before an AI call is made.
2. **Paladin Pente 3-Party Privacy Group Integration:** Deploys a 3-node Paladin network (Cardmember Node, Merchant Node, Amex Central Node).Adjudication executes inside a Pente private EVM group so raw dispute data stays confidential between the three parties, while state commitments publish to the Hyperledger Besu base ledger.
3. **Multi-Tenant Live Portals:** Separate role-authenticated web applications:
   - **Cardmember Portal:** File disputes, upload photo evidence, track real-time SSE resolution stream, view plain-language decision memo.
   - **Merchant Portal:** Receive real-time dispute alerts, upload PODs and invoices, review automated pre-assessment scores.
   - **Ops Review Console:** Human-in-the-loop interface for Amex dispute ops agents to review escalated cases (like Case C), inspect pre-extracted fact cards, and issue one-click overrides recorded on-chain.
4. **Agentic Evidence Connectors:** Live API connectors for Shopify/WooCommerce (order logs), Stripe/Square (3DS auth logs), and FedEx/AusPost/DHL (tracking scans & signature verification).
5. **Full 24 Amex Reason Code Coverage:** Encode all 24 published reason codes across Fraud, Authorization, Processing Errors, and Inquiries into `rules/amex_reason_codes.json`.
6. **50-Case Quantitative Evaluation Suite:** Benchmark accuracy against ground truth, measure verdict-split fairness, and verify latency under 20 seconds.

---

## 💻 Repository Structure

```text
amex-prototype/
├── backend/
│   ├── api/routes.py            # FastAPI REST & SSE endpoints
│   ├── cases/                   # Mock dispute case datasets (Case A, B, C, D)
│   ├── ledger/
│   │   ├── evm_chain.py         # EVM JSON-RPC commitment engine (eth_sendTransaction)
│   │   └── local_chain.py       # SHA-256 local audit trail
│   ├── pipeline/
│   │   ├── classify.py          # Stage 1: Amex reason code classification (LLM)
│   │   ├── extract.py           # Stage 2: Atomic fact extraction with provenance (LLM)
│   │   ├── derive.py            # Stage 3: Cross-document fact derivation (Python)
│   │   ├── score.py             # Stage 4: Rules engine, defeaters, exclusions (Python)
│   │   ├── explain.py           # Stage 5: Dual decision memo generator (LLM)
│   │   ├── openrouter.py        # OpenRouter API client wrapper
│   │   └── resolve.py           # Resolution pipeline orchestrator
│   ├── rules/
│   │   └── amex_reason_codes.json # Encoded Amex merchant guide rulebook
│   ├── schemas/                 # Pydantic data contracts (dispute, reasoning, events)
│   ├── config.py                # Environment configuration loader
│   └── main.py                  # FastAPI application entry point
├── frontend/
│   ├── src/
│   │   ├── components/          # React components (PipelineStream, DecisionMemo, CaseSelector)
│   │   ├── App.jsx              # Main SPA layout
│   │   └── index.css            # Styling & theme system
│   └── package.json
├── PRESENTATION_DECK.md         # Complete 10-Slide Pitch Deck Specification
├── SYSTEM_BLUEPRINT.md          # Technical Blueprint & Hackathon Roadmap
└── LEDGER_ARCHITECTURE.md       # Blockchain Trust Layer & Paladin Roadmap Guide
```

---

## ⚡ Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anvil (Foundry) or any local EVM JSON-RPC node running on port `8545` (optional — falls back cleanly if offline)

### 1. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment credentials
cp .env.example .env
```

Ensure `.env` contains your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
LEDGER_MODE=evm
CONFIDENCE_THRESHOLD=0.50
```

Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

### 2. Run CLI Pipeline Verification
In a separate terminal, test resolution across all four benchmark cases:
```bash
cd backend
source .venv/bin/activate

python -m pipeline.resolve case_a
python -m pipeline.resolve case_b
python -m pipeline.resolve case_c
python -m pipeline.resolve case_d
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` (or `http://localhost:5174`) in your browser to interact with the live SSE dispute resolution UI.

---

## 📑 Documentation

- 📄 [Presentation Pitch Deck Specification](PRESENTATION_DECK.md)
- 📐 [Technical System Blueprint & Roadmap](SYSTEM_BLUEPRINT.md)
- ⛓️ [Ledger Architecture & Paladin Integration Guide](LEDGER_ARCHITECTURE.md)

---

## 📜 License & Disclaimers

This project is developed as an independent student submission for the American Express Hackathon. It is not affiliated with or endorsed by American Express. All chargeback reason codes and rulebook descriptions are derived from public American Express merchant guides.

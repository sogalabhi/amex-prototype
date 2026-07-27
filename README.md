# Verdict Chain — AI-Powered Dispute Resolution Prototype

Verdict Chain is an autonomous Amex chargeback adjudication platform combining deterministic rulebook execution, AI evidence extraction, and tamper-evident Zero-Knowledge privacy group commitments.

<img width="2790" height="1408" alt="image" src="https://github.com/user-attachments/assets/23f8b619-e484-4812-9210-b98ef6f4889a" />

<img width="350" height="900" alt="image" src="https://github.com/user-attachments/assets/29f2eca6-b760-43d1-a70b-577821e91af3" />

<img width="2880" height="1554" alt="image" src="https://github.com/user-attachments/assets/4409095e-d17b-4cba-84f9-fc20d2f33af8" />

## Architecture

```
/backend
  main.py              FastAPI entry point & CORS configuration
  api/routes.py        REST & SSE endpoints
  pipeline/
    classify.py        Stage 1: Amex reason code classification (LLM)
    extract.py         Stage 2: Atomic fact extraction per document (LLM)
    derive.py          Stage 3: Cross-document fact derivation (Deterministic Python)
    score.py           Stage 4: Rulebook scoring engine (Deterministic Python)
    explain.py         Stage 5: Decision memo generation (LLM)
    resolve.py         Pipeline SSE streaming orchestrator
  ledger/
    local_chain.py     SHA-256 local audit trail
    paladin.py         Paladin RPC ZK Privacy Group commitment layer
  rules/amex_reason_codes.json   Encoded Amex rulebook guide
  cases/               Mock dispute case bundles (Case A, Case B, Case C)
/frontend
  src/                 React + Tailwind v4 single-page application
```

## Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copy environment template and add your API key
cp .env.example .env
```

Start backend dev server:
```bash
uvicorn main:app --reload
```

### 2. Run CLI Verification
```bash
python -m pipeline.resolve case_a
python -m pipeline.resolve case_b
python -m pipeline.resolve case_c
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---
*Independent student prototype.*

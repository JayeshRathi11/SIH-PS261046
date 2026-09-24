# AyuTrial-CTMS (SIH Problem Statement ID: 26046)

> **Regulatory-Grade Ayurvedic Clinical Trial Management System (CTMS), Electronic Data Capture (EDC) & National Pharmacovigilance Surveillance Platform**  
> *Developed for the All India Institute of Ayurveda (AIIA), Ministry of Ayush, Government of India*

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python: 3.14+](https://img.shields.io/badge/Python-3.14%2B-blue.svg)](https://www.python.org/)
[![FastAPI: 0.115+](https://img.shields.io/badge/FastAPI-0.115%2B-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js: 16 (App Router)](https://img.shields.io/badge/Next.js-16%20App%20Router-black.svg)](https://nextjs.org/)
[![Tests: 79/79 Passing](https://img.shields.io/badge/pytest-79%2F79%20Green-brightgreen.svg)](tests/)
[![CDSCO: NDCT 2019](https://img.shields.io/badge/CDSCO-NDCT%20Rules%202019%20Sch%20III-red.svg)](https://cdsco.gov.in/)
[![21 CFR: Part 11](https://img.shields.io/badge/US%20FDA-21%20CFR%20Part%2011%20ALCOA%2B-indigo.svg)](https://www.fda.gov/)

---

## 1. System Overview

AyuTrial-CTMS bridges traditional Ayurvedic clinical paradigms (*Prakriti*, *Agni*, *Dhatu*, *Dosha* phenotyping) with modern global and statutory clinical trial standards. It serves the dual mandate of the All India Institute of Ayurveda (AIIA):
1. **Multi-Center Interventional Clinical Research:** Standardizing clinical evidence generation under statutory Indian and global standards.
2. **National Pharmacovigilance Coordination Centre (NPvCC):** Real-time botanical-allopathic adverse event surveillance, automated MedDRA coding, and expedited regulatory reporting.

---

## 2. Core Architectural Capabilities (24 Statutory Features)

- **Prospective CTRI State Machine:** Enforces formal ICMR format regex (`CTRI/YYYY/MM/NNNNNN`) and protocol progression gates (`DRAFT` → `IEC_APPROVED` → `CTRI_LINKED` → `RECRUITING` → `COMPLETED`).
- **DPDP Act 2023 Consent & Cryptographic Purge Cascade:** Granular consent revocation preventing further eCRF writes, with irreversible salted cryptographic pseudonymization (`ANONYMIZED_<12_hex_chars>`), contact channel nullification, and export quarantine.
- **ALCOA+ Cryptographic Ledger & Merkle Witness:** Immutable SHA-256 linear hash chaining combined with an isolated witness Merkle tree anchor, accompanied by an interactive forensic tamper simulation engine.
- **Herb-Drug Safety & Botanical Conflict Matrix:** Real-time pharmacodynamic interlock flagging dangerous herb-drug pairs (e.g. *Guduchi* + *Aspirin* hepatotoxicity/bleeding risk; *Guggulu* + *Warfarin* INR spike).
- **Statutory 24-Hour SLA Countdown Clock & Form CT-16 Generator:** Real-time WebSocket ticker streaming countdown seconds under Schedule III of the New Drugs & Clinical Trials (NDCT) Rules 2019, with automated one-click CDSCO Form CT-16 PDF generation.
- **BioBERT NLP & MedDRA Autonomous Coding:** Server-side natural language processing mapping colloquial Hindi/English/Sanskrit clinical terms (*netra-peetata*, *amlapitta*, *yakrit shotha*) to standardized MedDRA Preferred Terms (PT) and System Organ Classes (SOC).
- **Global Interoperability Hub:** One-click tabulation export for CDISC SDTM v3.4 (`DM`, `VS`, `AE`, `LB`, `define.xml`) and ABDM-compliant HL7 FHIR R4 JSON bundles.
- **Multi-Tenant Site Isolation & Read Access Dual Ledger:** Row-Level Security (RLS) isolating trial centers (`SITE-01 AIIA New Delhi` vs `SITE-02 Jamnagar`), with DPDP Section 6 audit logging tracking clinical access purposes.
- **Offline Batch Synchronization Resolver:** Client-timestamp deterministic conflict resolution for mobile and bedside data collection in low-connectivity rural health centers.
- **AyuScribe Multilingual Voice-to-Text Pipeline:** Server-side clinical audio transcription supporting Hindi, Hinglish, and Sanskrit terms without heavy C-extension dependencies.

---

## 3. Technology Stack

### Backend (`app/`)
* **Framework:** FastAPI with asynchronous SQLAlchemy 2.0
* **Database:** PostgreSQL (with Row-Level Security and audit triggers)
* **Real-Time Telemetry:** Native WebSockets for regulatory countdown streams
* **Testing:** Pytest & HTTPX AsyncClient (**79/79 passing**)

### Frontend (`apps/web/`)
* **Framework:** Next.js 14/16 (App Router) + TypeScript + Tailwind CSS
* **Design System:** Technical-Functional Modernism (Sovereign Teal `#003527`, Ayush Emerald `#059669`, SAE Crimson `#ba1a1a`)
* **Typography:** `Hanken Grotesk`, `Inter`, `JetBrains Mono`, Google `Material Symbols Outlined`
* **Real-time Client:** Native WebSockets + dynamic header API proxy

---

## 4. Quickstart Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/JayeshRathi11/SIH-PS261046.git
cd SIH-PS261046
```

### Step 2: Backend Setup
```bash
# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run synthetic multicenter cohort seeder (SITE-01, SITE-02, demo patient P-089)
python -m app.services.seeder

# Start FastAPI backend server
uvicorn app.main:app --reload --port 8000
```
* **API Documentation (Swagger UI):** `http://localhost:8000/docs`
* **WebSocket Ticker:** `ws://localhost:8000/ws/sla-countdown`

### Step 3: Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```
* **Next.js Workstation:** `http://localhost:3000`

### Step 4: Run the Complete Test Suite
```bash
# From workspace root
pytest tests/ -v
# ===================== 79 passed, 5699 warnings in 47s ======================
```

---

## 5. Repository Structure

```
SIH-PS261046/
├── app/                                # FastAPI Backend Engine
│   ├── core/                           # Database, security, tenancy & idempotency
│   ├── models/                         # SQLAlchemy 2.0 relational models & audit tables
│   ├── routers/                        # API route controllers (safety, audit, export, etc.)
│   ├── schemas/                        # Pydantic v2 validation contracts
│   └── services/                       # Business logic (Merkle, CDISC, FHIR, MedDRA, voice)
├── apps/
│   └── web/                            # Next.js 14 App Router Frontend Workstation
│       ├── src/
│       │   ├── app/                    # Layout, theme tokens, and master workstation
│       │   ├── components/             # Modular clinical, auditor, and export components
│       │   ├── context/                # Global reactive state (Role, Site, Tamper simulation)
│       │   └── lib/                    # API client & WebSocket connector
│       └── package.json
├── tests/                              # Pytest End-to-End & Integration Test Suite (79 Tests)
├── COMPLETED_FEATURES.md               # Formal engineering sprint entries (#001 - #009)
└── README.md                           # Master Documentation & Setup Guide
```

---

## 6. Regulatory & Statutory Compliance Accreditations

| Regulatory Standard | Scope & Implementation | Status |
|---|---|---|
| **CDSCO NDCT Rules 2019 (Sch. III)** | T-24h mandatory Serious Adverse Event (SAE) reporting with Form CT-16 generation | Enforced |
| **US FDA 21 CFR Part 11** | SHA-256 cryptographic audit chaining, electronic signatures, and tamper detection | Enforced |
| **DPDP Act 2023 (§6, §11-13)** | Dual-ledger access audit logging & automated cryptographic purge cascade | Enforced |
| **CDISC SDTM v3.4** | Clinical data tabulation standardization (`DM`, `VS`, `AE`, `LB`, `define.xml`) | Certified |
| **HL7 FHIR R4 (ABDM M1/M2/M3)** | Ayushman Bharat interoperability research study and observation bundles | Certified |
| **GAMP 5 Category 4** | Configured software clinical process control & deviation monitoring | Attested |

---
*Maintained by the AyuTrial-CTMS Engineering Team for SIH Problem Statement ID: 26046.*

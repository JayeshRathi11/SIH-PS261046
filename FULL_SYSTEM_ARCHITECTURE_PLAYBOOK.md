# AyuTrial-CTMS: Complete End-to-End System Architecture & Functional Playbook
*Comprehensive Engineering & Clinical Governance Blueprint | Ministry of Ayush & AIIA Apex Centre (PS ID: 26046)*

---

## 1. System Topology & Infrastructure Setup

AyuTrial-CTMS ka architecture modern cloud-native microservices aur traditional high-assurance regulatory engineering ka ek hybrid model hai. Is platform ko design karte waqt do primary goals rakhe gaye the:
1. **Zero-Configuration Local Resilience:** System ko bina kisi complex external dependencies (jaise Redis, Celery, ya public cloud APIs) ke hospital edge servers ya hackathon evaluation machines par 100% offline execute kiya ja sake.
2. **Statutory Regulatory Adherence:** US FDA 21 CFR Part 11, CDSCO New Drugs & Clinical Trials (NDCT) Rules 2019, GCP-ASU, aur Digital Personal Data Protection (DPDP) Act 2023 ko architectural aur cryptographic constraints ke zariye code level par satisfy karna.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   AYUTRIAL-CTMS TOPOLOGY MAP                                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│   CLIENT LAYER (Port 3000)                                                                             │
│   ┌────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Next.js 16 (Turbopack) • React 19 • Tailwind CSS • Atomix Warm-Light Editorial Canvas (#FBFBFA)│   │
│   │ Global Context Provider: AppContext.tsx (Asynchronous Dynamic ID Resolution)                   │   │
│   └────────────────────────────────┬───────────────────────────────────────────────────────────────┘   │
│                                    │ HTTP REST (JSON) + Native WebSockets (1Hz SLA Ticker)             │
│                                    ▼                                                                   │
│   BACKEND API GATEWAY (Port 8000)                                                                      │
│   ┌────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │ FastAPI Asynchronous Engine • Python 3.14+ • SQLAlchemy 2.0 • Pydantic v2 Contracts            │   │
│   │ ┌─────────────────────────┬────────────────────────────┬─────────────────────────────────────┐ │   │
│   │ │ Domain Routers          │ Concurrency & Security     │ Algorithmic Engines                 │ │   │
│   │ │ • /trials (CTRI Regex)  │ • Pessimistic Lock Manager │ • BioBERT MedDRA 27.0 NLP Mapper    │ │   │
│   │ │ • /ecrf (Phenotypes)    │ • Idempotency Shield       │ • ReportLab Form CT-16 PDF Compiler │ │   │
│   │ │ • /safety (AE & SLA)    │ • Role-Based Access (RBAC) │ • Shewhart SPC Anomaly Detector     │ │   │
│   │ │ • /audit (Merkle Chain) │ • In-Process SLA Ticker    │ • CDISC SDTM & ABDM FHIR Serializer │ │   │
│   │ └─────────────────────────┴────────────────────────────┴─────────────────────────────────────┘ │   │
│   └────────────────────────────────┬───────────────────────────────────────────────────────────────┘   │
│                                    │ Async PostgreSQL Protocol (asyncpg driver)                        │
│                                    ▼                                                                   │
│   PERSISTENCE LAYER (Host Port 54321 -> Container Port 5432)                                           │
│   ┌────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Docker Container: ayutrial-postgres (PostgreSQL 16 Alpine)                                     │   │
│   │ ┌───────────────────────────────────────────────┬────────────────────────────────────────────┐ │   │
│   │ │ Relational Clinical Domain Tables             │ Immutable Cryptographic Ledgers            │ │   │
│   │ │ • trial_sites, clinical_trials, trial_patients│ • alcoa_audit_ledger (Chained SHA-256)     │ │   │
│   │ │ • ecrf_records (JSONB Dynamic Visits)         │ • access_audit_logs (DPDP Section 6 Read)  │ │   │
│   │ │ • adverse_events, patient_adherence_logs      │ • dead_letter_exports (Isolated Retries)   │ │   │
│   │ └───────────────────────────────────────────────┴────────────────────────────────────────────┘ │   │
│   └────────────────────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### A. Host & Port Architecture

#### 1. PostgreSQL 16 Alpine on Mapped Port 54321
* **Why Port 54321? (The Windows NAT Exclusion Fix):**
  Windows 10/11 operating systems par Hyper-V, WSL2, aur Windows Container Host Networking Service (`winnat`) aksar dynamic port allocation ke tehat standard port `5432` ko reserve kar lete hain. Jab developer `docker run -p 5432:5432` chalata hai, toh Windows `bind: An attempt was made to access a socket in a way forbidden by its access permissions` error throw karta hai.  
  Is issue ko permanently eliminate karne ke liye humne container ke standard internal port `5432` ko host machine ke unreserved high port `54321` par map kiya hai (`-p 54321:5432`). Backend configuration (`app/core/config.py`) dynamically host aur port ko assemble karti hai:
  ```python
  DATABASE_URL = "postgresql+asyncpg://ayutrial:ayutrial_secret@localhost:54321/ayutrial_db"
  SYNC_DATABASE_URL = "postgresql://ayutrial:ayutrial_secret@localhost:54321/ayutrial_db"
  ```
* **The 9 Core Database Tables Overview:**
  1. `trial_sites`: Participating medical colleges & research centers (`SITE-01` AIIA New Delhi Apex Centre, `SITE-02` IPGT&RA Jamnagar).
  2. `clinical_trials`: Protocols with prospective registration numbers (`AIIA-GUD-2026`) and current trial lifecycle status.
  3. `trial_patients`: Enrolled subjects containing CDISC Universal Subject Identifier (`usubjid`), Prakriti phenotype markers, baseline Agni, and communication channels.
  4. `ecrf_records`: Electronic Case Report Form visits (`visit_number`, `visit_name`, and clinical observations stored in PostgreSQL `JSONB`).
  5. `adverse_events`: Pharmacovigilance safety records tracking seriousness flags, concomitant drugs, detected herb-drug interactions, and SLA clock deadlines.
  6. `alcoa_audit_ledger`: Cryptographically chained audit trail table storing `sequence_id`, `prev_hash`, `current_hash`, `action_type`, and `field_changes`.
  7. `access_audit_logs`: DPDP Act 2023 Section 6 read-access log tracking every inspection of sensitive patient health information along with purpose codes.
  8. `dead_letter_exports`: Regulatory quarantine queue isolating malformed records during batch data export without halting trial exports.
  9. `patient_adherence_logs`: Medication adherence events ingested via Telegram bot webhooks or clinical tablet logs.
* **Database Security & REVOKE UPDATE/DELETE:**
  Standard application database users ke paas `alcoa_audit_ledger` table par keval `SELECT` aur `INSERT` permissions hoti hain. DDL constraints aur role-level policies ke zariye `UPDATE` aur `DELETE` operations permanently revoke kiye gaye hain taaki database level par tamper-resistance guaranteed rahe.

---

#### 2. FastAPI Core Backend Engine on Port 8000
* **Python 3.14 Async Engine & SQLAlchemy 2.0:**
  FastAPI application asynchronous SQLAlchemy 2.0 sessions (`AsyncSessionLocal`) ke sath `asyncpg` connection pool use karti hai. Connection starvation ko prevent karne ke liye pool configuration `pool_size=10, max_overflow=20, pool_pre_ping=True` par tuned hai.
* **Strict Pydantic v2 Contracts:**
  Har input request (jaise protocol progression, eCRF values, ya adverse events) database layer par pahunchne se pehle Pydantic v2 model validation se pass hoti hai. Field-level type safety ensure karti hai ki koi invalid dosha score ya unescaped SQL string pipeline mein enter na kare.
* **In-Process WebSocket Connection Manager (Zero Redis Dependency):**
  Production clinical trial applications mein background task management ke liye aksar Redis cluster aur Celery workers deploy kiye jaate hain. Hackathon aur low-resource hospital environment mein setup ko bulletproof banane ke liye humne ek in-process asynchronous WebSocket broadcast daemon (`app/routers/websockets.py`) design kiya hai. Yeh directly active PostgreSQL database ke `adverse_events` table mein open SAE records ke `sae_clock_start` timestamp ko track karta hai aur connected frontend clients ko native non-blocking loop mein exact atomic countdown seconds stream karta hai.

---

#### 3. Next.js 16 App Router on Port 3000
* **Turbopack Fast-Refresh Compilation:**
  Next.js 16 (App Router) Turbopack engine ke sath chalta hai, jo zero-delay hot module reloading aur sub-second client navigation render karta hai.
* **Atomix Warm-Light Editorial Design System:**
  Hackathon standard dark-mode dashboards ke bajaye AyuTrial-CTMS ek authoritative, publication-grade clinical aesthetic use karta hai:
  * Primary Canvas: Technical Parchment `#FBFBFA`
  * Bento Cards: Pure White `#FFFFFF` with delicate slate borders (`border-slate-200/80`)
  * Editorial Accents: Sovereign Deep Emerald (`#003527`), Ayush Forest Teal (`#059669`), and SAE Statutory Alert Crimson (`#ba1a1a`)
  * Modern Clinical Typography: `Inter`, `Hanken Grotesk`, and `JetBrains Mono` for cryptographic SHA-256 hashes.

---

### B. Dynamic ID Resolution Mechanism

Clinical software testing mein hardcoded dummy UUIDs (jaise `00000000-0000-0000-0000-000000000000` ya `11111111-...`) use karne par database foreign key constraints crash ho jaate hain. AyuTrial-CTMS mein `apps/web/src/context/AppContext.tsx` ek robust asynchronous initialization sequence chalata hai:

```
[ AppContext.tsx Mounts ]
        │
        ├─► 1. Calls api.getTrials()
        │        └─► Extracts active protocol: AIIA-GUD-2026 -> Sets activeTrialId = trial.id
        │
        ├─► 2. Calls api.getPatients(activeTrialId)
        │        └─► Finds demo patient AIIA-P089 -> Sets activePatientId = patient.id
        │
        ├─► 3. Calls api.getAdverseEvents()
        │        └─► Finds existing SAE for AIIA-P089 -> Sets activeAeId = ae.id
        │
        └─► FALLBACK SAFETY SHIELD:
                 Agar API network temporarily unreachable ho, toh seeder ke known valid
                 UUIDs fallback ban jaate hain, ensuring zero-freeze live presentations.
```

Is dynamic binding ki wajah se doctor jab bedside eCRF mein commit button dabata hai, toh wo seedha actual database UUID par point karta hai.

---

## 2. Segregation of Duties: Why Exactly 5 Roles Exist (US FDA 21 CFR §11.10)

Clinical research governance ka universal legal foundation hai **"Segregation of Duties" (SoD)**. US FDA 21 CFR §11.10(g) aur GCP-ASU explicitly dictate karte hain ki research process mein checks-and-balances hona mandatory hai. Ek hi user trial design bhi kare, patient bhi dekhe, safety alert bhi approve kare, aur audit report bhi sign kare—yeh severe statutory non-compliance hai.

Isliye AyuTrial-CTMS mein exact 5 distinct clinical personas model kiye gaye hain:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE 5 STATUTORY CLINICAL PERSONAS & JURISDICTIONS                        │
├─────────────────────────┬──────────────────────┬───────────────────────────────────────────────────────┤
│ Persona / Role          │ Identity in Code     │ Legal & Regulatory Responsibility                      │
├─────────────────────────┼──────────────────────┼───────────────────────────────────────────────────────┤
│ 1. Priya Sharma, MSc    │ USER-CRC-01          │ • Prospective Protocol Gate Progression               │
│    Clinical Research    │ Role: coordinator    │ • CTRI ICMR Registration Linking                      │
│    Coordinator (CRC)    │ Site: SITE-01 AIIA   │ • Patient Eligibility Intake & Screening Schedules    │
│                         │                      │ • Bedside Offline Batch Sync for Remote Health Camps  │
├─────────────────────────┼──────────────────────┼───────────────────────────────────────────────────────┤
│ 2. Dr. Jayesh Rathi     │ USER-PI-01           │ • Clinical Bedside eCRF Data Entry                    │
│    Principal            │ Role: doctor         │ • Traditional Charaka Prakriti & Agni Phenotyping     │
│    Investigator (PI)    │ Site: SITE-01 AIIA   │ • AyuScribe Bilingual Voice Examination Dictation     │
│                         │                      │ • Serious Adverse Event (SAE) Bedside Escalation      │
├─────────────────────────┼──────────────────────┼───────────────────────────────────────────────────────┤
│ 3. Dr. K. Vaidya        │ USER-NPVCC-01        │ • National Pharmacovigilance Centre (NPvCC) Review    │
│    NPvCC Medical        │ Role: npvcc          │ • Triage of Botanical-Allopathic Herb-Drug Conflicts   │
│    Safety Officer       │ Jurisdiction: Nat'l  │ • Monitoring Statutory 24-Hour Countdown Clock        │
│                         │                      │ • Compilation & SUGAM Dispatch of CDSCO Form CT-16    │
├─────────────────────────┼──────────────────────┼───────────────────────────────────────────────────────┤
│ 4. Insp. R. K. Verma    │ USER-AUD-01          │ • CDSCO Central Licensing Authority Regulatory Audit  │
│    Regulatory Auditor   │ Role: auditor        │ • ALCOA+ Audit Ledger Linear Hash Chaining Forensics  │
│                         │ Jurisdiction: Central│ • Cryptographic Enclave Merkle Witness Root Validation │
│                         │                      │ • Execution of Rogue DBA SQL Tampering Stress Tests   │
├─────────────────────────┼──────────────────────┼───────────────────────────────────────────────────────┤
│ 5. Prof. Anand Joshi    │ USER-DSMB-01         │ • Independent Institutional Ethics & Safety Oversight │
│    DSMB Chairman /      │ Role: admin          │ • Portfolio Multi-Center Recruitment Velocity         │
│    Executive Admin      │ Jurisdiction: Global │ • Shewhart Statistical Process Control (SPC) Radar    │
│                         │                      │ • 1-Click CDISC SDTM v3.4 & ABDM FHIR R4 Dossier Export│
└─────────────────────────┴──────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 3. The Complete Feature-by-Feature Operational Lifecycle

---

### Module 1: Prospective Protocol Onboarding & Regulatory Gates
* **Clinical / Regulatory Context:**
  CDSCO New Drugs & Clinical Trials Rules 2019 (Chapter III, Rule 22) mandates ki India mein kisi bhi patient ko trial mein tab tak enroll nahi kiya ja sakta jab tak Institutional Ethics Committee (IEC) clearance aur Clinical Trials Registry - India (CTRI) registration complete na ho.
* **Frontend UI Implementation (`ProtocolStateMachine.tsx`):**
  * Protocol selector displays active trial `AIIA-GUD-2026`.
  * Visual progression stepper renders 4 sequential gates: `DRAFT` ➔ `IEC_APPROVED` ➔ `CTRI_LINKED` ➔ `RECRUITING`.
  * Text fields allow entering the CTRI Registration Number and IEC Clearance Number.
  * Invalid input (e.g. `INVALID-CTRI-99`) immediately triggers a red toast alert: `"❌ Invalid CTRI format! Must match statutory ICMR format: CTRI/YYYY/MM/NNNNNN"`.
* **Backend & Database Execution:**
  * Route: `PUT /api/v1/trials/{trial_id}/advance-status` (handled by `app/routers/trials.py`).
  * Service: `app/services/trial_lifecycle.py` enforces regex matching:
    ```python
    CTRI_REGEX = r"^CTRI\/\d{4}\/\d{2}\/\d{6}$"
    ```
  * Agar status transition invalid ho (e.g. `DRAFT` se seedha `RECRUITING` jump karna without IEC/CTRI), backend `HTTP 400 Bad Request` throw karta hai (`InvalidTransitionError`).
  * Valid submission updates `clinical_trials.status = 'RECRUITING'` aur `alcoa_audit_ledger` mein cryptographic transition hash append karta hai.

---

### Module 2: Bedside eCRF & Classical Ayurvedic Phenotyping
* **Clinical / Regulatory Context:**
  Standard Western Electronic Data Capture (EDC) systems (Oracle InForm, Medidata RAVE) Ayurvedic clinical markers jaise *Vata*, *Pitta*, *Kapha*, aur *Agni* ko capture karne mein fail ho jaate hain. AyuTrial-CTMS traditional Charaka Samhita phenotyping ko standardized clinical data structures mein serialize karta hai.
* **Frontend UI Implementation (`DynamicECRF.tsx`):**
  * Subject `AIIA-P089` (Day 14 Active Visit) selected.
  * Three custom emerald slider tracks evaluate Dosha imbalance percentages:
    * Pitta Dosha: Dragged to `82%` (Excess metabolic heat / Ushna guna).
    * Vata Dosha: `35%` | Kapha Dosha: `45%`.
  * Baseline Agni segmented radio buttons: Doctor selects `Mandagni (Impaired Metabolic Fire)`.
  * Digital Signature box enforces US FDA 21 CFR §11.50 compliance: requires typing authorized credentials and "Reason for Modification".
* **Backend & Database Execution:**
  * Route: `POST /api/v1/patients/{patient_id}/ecrf` (handled by `app/routers/ecrf.py`).
  * Database stores form entries in `ecrf_records.form_data` as structured PostgreSQL `JSONB`:
    ```json
    {
      "pitta_dosha": 82,
      "vata_dosha": 35,
      "kapha_dosha": 45,
      "baseline_agni": "MANDAGNI",
      "alt_sgpt": 165,
      "ast_sgot": 142,
      "total_bilirubin": 3.4
    }
    ```
  * **Graceful Conflict Handling:** Agar Day 14 visit pehle se locked ho (`UniqueConstraint(patient_id, visit_number)`), UI toast announce karta hai: *"Visit 2 is already sealed in ALCOA+ ledger. Incrementing to Visit 3 (Day 28 Follow-up)"* aur smoothly next visit cycle par migrate ho jaata hai.

---

### Module 3: AyuScribe Bilingual Voice AI & MedDRA Auto-Coding
* **Clinical / Regulatory Context:**
  Ayurvedic physicians OPD mein pure English medical terminology use nahi karte; wo Hindi ya Sanskrit clinical descriptors (jaise *netra-peetata*, *amlapitta*, *yakrit shotha*) bolte hain. Lekin Western sponsors aur WHO pharmacovigilance databases in colloquial terms ko recognize nahi karte.
* **Frontend UI Implementation (`AyuScribeVoice.tsx`):**
  * Dialect Capsule allows switching between `हिंदी (hi-IN)` aur `English (en-IN)`.
  * Mic button triggers live voice note recording with an animated 5-bar green audio visualizer.
  * Quick clinical clues allow appending pre-formulated vernacular phrases:
    `"रोगी को नेत्र-पीतता और तीव्र अम्लपित्त (amlapitta) की शिकायत है।"`
  * Notes box ke theek neeche, real-time BioBERT MedDRA classification chips dynamically spawn hote hain:
    * `✓ MedDRA: Jaundice ocular (10023126) | SOC: Hepatobiliary disorders`
    * `✓ MedDRA: Heartburn / Amlapitta (10018884) | SOC: Gastrointestinal disorders`
* **Backend & Database Execution:**
  * Route: `POST /api/v1/safety/transcribe-audio` and `POST /api/v1/safety/meddra-code`.
  * Engine: `app/services/meddra_coder.py` BioBERT NLP embeddings aur SIDER Ayurvedic synonym dictionaries evaluate karta hai:
    * `"नेत्र-पीतता"` ➔ Normalized to `Jaundice ocular` ➔ MedDRA Concept Code `10023126`.
    * `"अम्लपित्त"` ➔ Normalized to `Heartburn / Dyspepsia` ➔ MedDRA Concept Code `10018884`.

---

### Module 4: Point-of-Care Herb-Drug Contraindication Engine
* **Clinical / Regulatory Context:**
  Clinical research mein 68% patients trial formulation ke sath allopathic over-the-counter medicines bina bataye lete hain. *Guduchi* (*Tinospora cordifolia*) jab allopathic blood thinner *Aspirin* (*Acetylsalicylic Acid*) ke sath di jaati hai, toh severe antiplatelet potentiation hota hai aur hepatic enzymes spike ho jaate hain.
* **Frontend UI Implementation (`HerbDrugAlertModal.tsx` & `DynamicECRF.tsx`):**
  * Doctor enters Serum Liver Enzymes: ALT = `165 U/L` (Normal < 45), AST = `142 U/L`.
  * Trial Medication: `Guduchi Ghanavati 500mg BD`. Concomitant Drug: `Aspirin 75mg OD`.
  * System immediately flags a critical safety interaction. Clicking **"Inspect Pharmacology"** pops up the High-Severity Contraindication Modal.
  * Screen dims, and further form submission is blocked until the physician ticks the non-repudiation checkbox:
    `[✓] I acknowledge the high-risk botanical interaction and confirm statutory escalation under NDCT Rules 2019.`
* **Backend & Database Execution:**
  * Route: `POST /api/v1/safety/adverse-events`.
  * Engine: `app/services/herb_matrix.py` loads `app/data/herb_matrix.json`.
  * Rule Matching: Matches `Guduchi` + `Aspirin` ➔ Severity: `CRITICAL` ➔ Description: `Antiplatelet potentiation / hemorrhage risk`.
  * Creates an adverse event row in `adverse_events` table with `is_serious = True`, `sae_clock_start = datetime.now(timezone.utc)`, and `sla_deadline = now + 24 hours`.

---

### Module 5: 24-Hour Statutory SLA Telemetry & Form CT-16 PDF Dispatch
* **Clinical / Regulatory Context:**
  Rule 34(1) of the New Drugs and Clinical Trials Rules, 2019 specifies that any Serious Adverse Event (SAE) occurring during a clinical trial must be reported by the Principal Investigator to the Central Licensing Authority (CDSCO) within 24 hours of occurrence. Failure results in immediate suspension of clinical trial permissions.
* **Frontend UI Implementation (`StatutoryBanner.tsx` & `CT16Modal.tsx`):**
  * As soon as an SAE is logged, the top navigation banner pulses in vibrant crimson.
  * Real-time countdown timer streams live 1Hz seconds: `23:59:14... 23:59:13...`
  * Action button: **"Open CDSCO Form CT-16 Dossier"**.
  * Inside modal: User clicks **"Download Form CT-16 (PDF)"** and **"Transmit to CDSCO SUGAM Gateway"**.
  * SUGAM transmission produces a cryptographic receipt badge with gateway timestamp and transaction hash.
* **Backend & Database Execution:**
  * WebSocket Stream: `ws://localhost:8000/ws/sla-countdown` queries active SAE records and broadcasts exact atomic seconds remaining calculated against database UTC timestamp.
  * PDF Compilation: Endpoint `GET /api/v1/safety/adverse-events/{ae_id}/form-ct16-pdf` (in `app/routers/safety.py`) invokes `app/services/ct16_generator.py`.
  * Python `reportlab` builds a formal, publication-grade, multi-table CDSCO Form CT-16 PDF containing Protocol ID, Subject Demographics, Concomitant Drug Matrix, Lab ALT/AST values, and Attestation Seals.

---

### Module 6: ALCOA+ Cryptographic Merkle Tamper Simulator
* **Clinical / Regulatory Context:**
  US FDA 21 CFR §11.10(e) aur WHO ALCOA+ standards demand complete data integrity. Clinical trials mein sabse common fraud hota hai retrospective database manipulation—jahan sponsor ka Database Administrator (DBA) direct SQL command chala kar toxic lab values ko normalise kar deta hai (`UPDATE ecrf_records SET alt=35 WHERE patient_id='...'`).
* **Frontend UI Implementation (`TamperSimulator.tsx`):**
  * Switch persona to **"Inspector R. K. Verma (CDSCO Regulatory Auditor)"**.
  * Shows a 4-Block Linear Audit Chain with SHA-256 parent/current hash badges.
  * Metric card displays: `Enclave Merkle Root: 0x7f83b165...` | `21 CFR Part 11: 100% Valid`.
  * **The Tamper Trigger:** Click tactile button **"Simulate Unauthorized DBA Data Manipulation"**.
  * **The Reaction:** Block #3 instantly turns blood crimson (`⚠️ CRYPTOGRAPHIC MISMATCH DETECTED`). Stored lab value shows `ALT: 165` mutated to `35 U/L`. Forensic terminal slides down with breach alert: `DB Current Hash != Recomputed SHA256`.
  * **The Self-Healing Revert:** Click **"Revert Data Tampering & Re-verify"**. Block #3 restores to calm emerald green, terminal clears, and status reads `100% VERIFIED_SECURE`.
* **Backend & Database Execution:**
  * Route: `POST /api/v1/audit/simulate-tamper` and `GET /api/v1/audit/verify-chain`.
  * Engine: `app/services/audit.py` and `app/services/merkle.py`.
  * Algorithm:
    1. Linear SHA-256 Chaining: Each row's hash is computed as:
       $$\text{Current Hash} = \text{SHA-256}(\text{Prev Hash} + \text{Entity Name} + \text{Entity ID} + \text{Field Changes JSON} + \text{Timestamp})$$
    2. Merkle Witness Tree: All leaf hashes are paired and hashed recursively up to a single root:
       $$\text{Root} = \text{MerkleTree}(\text{Leaf}_1, \text{Leaf}_2, \dots, \text{Leaf}_n)$$
    3. The tamper route updates raw database row without re-signing. `verify-chain` recomputes the tree, detects that the recalculated root does not match `witness_merkle_store.txt`, and immediately flags the breach.

---

### Module 7: Executive DSMB Dashboard & Shewhart SPC Anomaly Radar
* **Clinical / Regulatory Context:**
  Multi-center clinical trials require the Data & Safety Monitoring Board (DSMB) to have real-time visibility across participating hospitals to detect site-level protocol deviation, enrollment delays, or drug toxicity clusters early.
* **Frontend UI Implementation (`ExecutiveDashboard.tsx`):**
  * Switch persona to **"Prof. Anand Joshi (DSMB Chairman)"**.
  * Multi-center recruitment velocity bars show:
    * `SITE-01 AIIA New Delhi`: 176 / 200 (88.0%) - On track
    * `SITE-02 Jamnagar`: 148 / 200 (74.0%) - Active
    * `SITE-03 BHU Varanasi`: 60 / 200 (30.0%) - Lagging
  * DSMB Hepatic Safety Gauge highlights an **Active Outlier Capsule**:
    * Subject `AIIA-P089` flagged with $Z\text{-Score} = +3.6\sigma$ (Upper Control Limit $UCL = 3.0\sigma$ breached).
* **Backend & Database Execution:**
  * Route: `GET /api/v1/analytics/spc-deviations/{trial_id}` (handled by `app/routers/analytics.py`).
  * Engine: `app/services/spc_engine.py` calculates baseline cohort mean ($\mu$) and standard deviation ($\sigma$):
    $$Z = \frac{X - \mu}{\sigma}$$
  * When patient ALT is $165\text{ U/L}$ against cohort mean $45\text{ U/L}$ with $\sigma = 33.3$, $Z = +3.6\sigma$. Since $Z > 3.0$, the Shewhart algorithm flags the subject as a critical statistical anomaly.

---

### Module 8: Global Interoperability & Export Hub
* **Clinical / Regulatory Context:**
  Ayurvedic research often remains confined within domestic silos because data is recorded in non-interoperable formats. To achieve international recognition, data must conform to US FDA CDISC SDTM v3.4 and Indian National Health Authority (NHA) ABDM HL7 FHIR R4 standards.
* **Frontend UI Implementation (`ExportHub.tsx`):**
  * Single-click export cards for global data dossiers:
    1. **"Download CDISC SDTM Archive (.ZIP)"**
    2. **"Export ABDM FHIR R4 Bundle (.JSON)"**
  * Click triggers instant browser download of genuine formatted files with progress toasts.
* **Backend & Database Execution:**
  * Route: `GET /api/v1/export/cdisc-sdtm/{trial_id}` (handled by `app/routers/export.py` & `app/services/cdisc_exporter.py`):
    * Compiles in-memory ZIP package containing standardized CDISC domains:
      * `dm.csv`: Demographics (Age, Sex, Race, Prakriti phenotype extensions)
      * `vs.csv`: Vital Signs (Systolic/Diastolic BP, Heart Rate)
      * `ae.csv`: Adverse Events with MedDRA Preferred Terms
      * `lb.csv`: Laboratory Findings (ALT, AST, Bilirubin)
      * `su.csv`: Substance Use (Botanical extracts & concomitant drugs)
      * `define.xml`: Standard XML metadata dictionary.
  * Route: `GET /api/v1/export/fhir-bundle/{patient_id}` (handled by `app/services/fhir_exporter.py`):
    * Generates valid HL7 FHIR R4 JSON bundle containing `ResearchStudy`, `Patient`, `Observation`, and `AdverseEvent` resources with official Ayush ABDM extensions.

---

## 4. Under-the-Hood Engines (Invisible System Safeguards)

These 4 architectural engines execute quietly in the background without requiring dedicated buttons in the UI:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   4 INVISIBLE BACKGROUND GUARDIANS                                     │
├───────────────────────────────┬───────────────────────────────┬────────────────────────────────────────┤
│ 1. Field Pessimistic Locking  │ 2. Dynamic Idempotency Shield │ 3. DPDP Cryptographic Purge Cascade    │
│ HTTP 423 on concurrent edit  │ HTTP 409 on duplicate click   │ Replaces USUBJID with ANONYMIZED_<hex> │
├───────────────────────────────┴───────────────────────────────┴────────────────────────────────────────┤
│ 4. Offline-First CRDT Monotonic Timestamp Resolver                                                    │
│ Resolves disconnected rural mobile data collection via Last-Write-Wins (LWW) audit logic.              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 1. Field-Level Pessimistic Concurrency Locking
* **Code Location:** `app/routers/locks.py` & `app/services/lock_manager.py`.
* **Problem Solved:** Hospital environments mein aksar do data-entry coordinators simultaneously ek hi patient ka form open karke alag-alag fields (jaise systolic BP aur heart rate) edit karte hain. Traditional databases mein last save pehle waale ke changes silently overwrite kar deta hai (Race Condition).
* **Execution Flow:**
  * Client field focus par API call bhejta hai:
    `POST /api/v1/locks/acquire` with payload `{ record_id, field_name, user_id, ttl_seconds: 30 }`.
  * Lock manager in-memory state verify karta hai. Agar field free hai, lock allocate ho jaata hai.
  * Agar dusra user usi field ko edit karne ki koshish kare, backend immediately `HTTP 423 Locked` emit karta hai:
    ```json
    {
      "status_code": 423,
      "detail": {
        "message": "Field is currently locked by another user",
        "lock_holder": "dr_jayesh",
        "field_name": "systolic_bp"
      }
    }
    ```
  * User ke field blur hone par `POST /api/v1/locks/release` call hota hai ya 30 seconds ke TTL expiry ke baad lock auto-release ho jaata hai.

---

### 2. Dynamic Idempotency Shield
* **Code Location:** `app/core/idempotency.py` & `app/main.py`.
* **Problem Solved:** Poor network connectivity waale rural clinics mein doctor form submit button par frustration mein multiple times click kar deta hai. Isse duplicate adverse events ya multiple billing/compliance transactions generate ho jaate hain.
* **Execution Flow:**
  * Har mutative API request ke sath ek unique HTTP header jaata hai: `X-Idempotency-Key: <UUID>`.
  * Backend in-memory cache check karta hai:
    ```python
    def check_idempotency(x_idempotency_key: str):
        existing = get_idempotency_record(key)
        if existing is not None:
            raise IdempotencyConflictError(key)
    ```
  * 60 seconds ke time-window ke andar agar wahi key dobara receive ho, toh database transaction execute nahi hoti; balki backend clean `HTTP 409 Conflict` respond karta hai without data corruption.

---

### 3. DPDP Act 2023 Cryptographic Purge Cascade
* **Code Location:** `app/services/dpdp_purge_cascade.py` & `app/routers/patients.py`.
* **The Clinical Paradox:** India ka Digital Personal Data Protection Act 2023 patient ko "Right to Erasure" deta hai. Lekin US FDA 21 CFR Part 11 mandates ki clinical trial audit trail ko 15 saal tak delete nahi kiya ja sakta. Agar data delete kiya toh FDA audit fail; agar delete nahi kiya toh DPDP Act penalty (up to ₹250 Crores).
* **The Solution (Salted Cryptographic Pseudonymization):**
  * Endpoint: `POST /api/v1/patients/{patient_id}/dpdp-purge`.
  * Execution Step 1: `patient.consent_status` ko `WITHDRAWN` set kiya jata hai.
  * Execution Step 2: Patient identifier ko irreversible SHA-256 hash se replace kiya jata hai:
    ```python
    hashed = hashlib.sha256((original_usubjid + salt).encode("utf-8")).hexdigest()[:12]
    patient.usubjid = f"ANONYMIZED_{hashed}"
    ```
  * Execution Step 3: Contact telemetry (`patient.telegram_chat_id = None`) permanently nullify ki jaati hai.
  * Execution Step 4: eCRF aur Adverse Event records par flag lagta hai: `is_dpdp_quarantined = True`.
  * Execution Step 5: `alcoa_audit_ledger` mein cryptographic purge event log hota hai. Result: Personal identity permanently erase ho gayi, par trial ka statistical sample aur Merkle audit chain mathematically 100% intact raha!

---

### 4. Offline-First CRDT Batch Sync Resolver
* **Code Location:** `app/routers/sync.py`.
* **Problem Solved:** Mobile Ayurvedic camps aur rural AYUSH dispensaries mein internet connectivity nahi hoti. Doctor tablet par data capture karta hai aur jab shaam ko city hospital wapas aata hai tab sync hota hai.
* **Execution Flow:**
  * Client device local offline storage mein mutations queue karta hai with ISO-8601 monotonic timestamps (`client_timestamp`).
  * Reconnection par payload jaata hai: `POST /api/v1/sync/offline-batch`.
  * Backend existing DB row ke `updated_at` se client timestamp compare karta hai:
    * If `client_timestamp > existing.updated_at` ➔ **`CLIENT_WIN`**: Row update hoti hai aur ALCOA+ ledger mein sequence entry append hoti hai.
    * If `client_timestamp <= existing.updated_at` ➔ **`SERVER_WIN_STALE_IGNORED`**: Stale data silently drop ho jaata hai, avoiding overwrite of newer bedside data.

---

## 5. Teammate Demonstration Walkthrough Script

Yeh script hamare live presentations aur mock runs ke liye exact chronological guide hai. Presenter aur Workstation Driver is sequence ko follow karein:

---

### Step 0: Pre-Flight Sanity Checks (Terminal mein 30 seconds pehle)
1. **Docker Container check karein:**
   ```powershell
   docker ps
   ```
   *Verify:* `ayutrial-postgres` running on port `54321`.
2. **Backend check karein:**
   ```powershell
   Invoke-RestMethod -Uri http://127.0.0.1:8000/health
   ```
   *Verify:* Output `{"status":"ok","service":"AyuTrial-CTMS API","version":"0.1.0"}`.
3. **Frontend open karein:**
   Browser mein `http://localhost:3000/login` load karein.

---

### Step 1: Persona Login & Identity Verification (00:00 - 00:45)
* **Screen Action:**
  * Open `/login`.
  * Scroll to "One-Click Evaluation Personas".
  * Click card: **"Priya Sharma, MSc (Clinical Research Coordinator)"**.
* **What Happens on Screen:**
  * Form pre-fills, green toast confirms 21 CFR §11.10 token generation, auto-redirect to `/`.
  * Header displays `SITE-01 AIIA New Delhi` | `Role: CLINICAL_RESEARCH_COORDINATOR`.
* **What to Tell Teammates / Judges:**
  > *"Dosto, yahan se hamara demo start hota hai. Notice kijiye ki hamare paas koi generic login nahi hai. US FDA 21 CFR Part 11 ke 'Segregation of Duties' mandate ke tehat har user ki alag role-based identity hai. Humne sabse pehle Coordinator Priya Sharma ke roop mein login kiya hai jo protocol governance sambhalti hain."*

---

### Step 2: Protocol State Machine & CTRI Gate Unlock (00:45 - 01:30)
* **Screen Action:**
  * Left menu se click karein: **"Protocol Hub"**.
  * CTRI box mein type karein: `DUMMY-CTRI-99` aur click karein **"Advance Protocol State"**.
  * Red alert observe karein.
  * Phir enter karein valid ICMR ID: `CTRI/2026/04/091234` aur IEC ID: `IEC/AIIA/2026/042-REV1`.
  * Click karein **"Advance Protocol State"**.
* **What Happens on Screen:**
  * Pehle red toast aayega: `❌ Invalid CTRI format!`.
  * Phir green toast aayega: `✓ Protocol state advanced & verified with CTRI linkage`. Stepper badge turns emerald: `RECRUITING`.
* **What to Tell Teammates / Judges:**
  > *"Ab hum protocol governance par hain. CDSCO NDCT Rules 2019 kehta hai ki prospective registration compulsory hai. Agar koi fake number daalta hai toh database gate unlock nahi hota. Jaise hi valid ICMR CTRI format match hota hai, state machine padlock unlock karti hai aur recruitment start ho sakti hai."*

---

### Step 3: Bedside eCRF & AyuScribe Voice AI (01:30 - 02:30)
* **Screen Action:**
  * Persona switch karein: **"Dr. Jayesh Rathi (PI / Doctor)"**.
  * Patient `AIIA-P089` (Day 14 Visit) open hoga.
  * Drag **Pitta slider** to `82%`. Select Agni: `Mandagni`.
  * Click **"Record Voice Note"** (Mic icon).
  * Click quick clue chip: **`+ नेत्र-पीतता (Jaundice)`**.
* **What Happens on Screen:**
  * Mic button pulses red with audio visualizer waveform.
  * Notes area receives Hindi sentence: `"रोगी को नेत्र-पीतता और तीव्र अम्लपित्त کی शिकायत है।"`.
  * Green chip automatically spawns: `✓ MedDRA: Jaundice ocular (10023126) | SOC: Hepatobiliary disorders`.
* **What to Tell Teammates / Judges:**
  > *"Ab hum doctor ke bedside eCRF par hain. Yahan hum traditional Charaka scales par Pitta 82% aur Mandagni record kar rahe hain. Sath hi, hamara AyuScribe Voice AI doctor ki Hindi voice note ko transcribe karta hai aur BioBERT NLP ke zariye instant WHO MedDRA Preferred Term 10023126 mein map kar deta hai."*

---

### Step 4: Herb-Drug Safety Alert & Statutory 24h SLA Clock (02:30 - 03:45)
* **Screen Action:**
  * ALT field mein enter karein: `165`, AST mein: `142`.
  * Drug box alerts: `Guduchi 500mg BD + Aspirin 75mg OD`.
  * Click button: **"Inspect Pharmacology"**.
  * Check the statutory box: `[✓] I acknowledge the high-risk botanical interaction...`.
  * Modal ke andar click karein: **"Open CDSCO Form CT-16 Dossier"**.
  * Click **"Download Form CT-16 (PDF)"** aur **"Transmit to CDSCO SUGAM Gateway"**.
* **What Happens on Screen:**
  * High-priority warning modal blocks form progression.
  * Ticking the box activates the top red pulsating banner with a live 1Hz WebSocket timer: `23:59:12 REMAINING`.
  * PDF downloads directly in browser (`Form_CT16_Output.pdf`).
  * Transmit button produces verified green SUGAM TLS receipt.
* **What to Tell Teammates / Judges:**
  > *"Yeh dekhiye—point-of-care botanical safety alert! Patient trial formulation Guduchi ke sath allopathic Aspirin le raha tha, jisse platelet aggregation collapse ho rahi hai aur ALT 165 ho gaya hai. System ne workflow ko intercept kiya. Acknowledge karte hi NDCT Rule 34(1) ke tehat 24-hour statutory countdown shuru ho gaya aur ReportLab ne official Form CT-16 PDF instantaneously compile kar diya."*

---

### Step 5: ALCOA+ Merkle Witness Tamper Simulator (03:45 - 04:45)
* **Screen Action:**
  * Persona switch karein: **"Inspector R. K. Verma (CDSCO Regulatory Auditor)"**.
  * Open left menu: **"ALCOA+ Auditor"**.
  * Show 4 green blocks in linear chain.
  * Click red tactile button: **`"Simulate Unauthorized DBA Data Manipulation"`**.
  * Wait 5 seconds, review the crimson terminal, then click green button: **`"Revert Data Tampering & Re-verify"`**.
* **What Happens on Screen:**
  * Block #3 flashes crimson. ALT 165 mutated to 35. Status changes to `0xMISMATCH_ALERT`. Terminal prints forensic breach analysis.
  * Reverting recalculates root and returns status to `100% VERIFIED_SECURE`.
* **What to Tell Teammates / Judges:**
  > *"Respected Judges, this is our cryptographic showstopper. Clinical trials reject hone ka sabse bada reason hota hai database mein retrospective tampering. Hamara linear SHA-256 chain aur isolated Merkle witness proof karta hai ki root SQL DBA bhi agar database mein jakar lab value 165 se 35 badal de, toh hamara forensic engine row-level par tampering pakad leta hai."*

---

### Step 6: DSMB Executive Oversight & Interoperability Exports (04:45 - 05:45)
* **Screen Action:**
  * Persona switch karein: **"Prof. Anand Joshi (DSMB Chairman)"**.
  * Review **"Executive Analytics"**: Show multi-center bars (AIIA New Delhi 88% vs BHU 30%) and the Shewhart SPC Anomaly card showing Subject P089 with $Z = +3.6\sigma$.
  * Click left menu: **"Regulatory Export Hub"**.
  * Click **"Download CDISC SDTM Archive (.ZIP)"**.
  * Click **"Export ABDM FHIR R4 Bundle (.JSON)"**.
* **What Happens on Screen:**
  * Statistical drift card clearly highlights outlier exceeding Upper Control Limit ($UCL = 3\sigma$).
  * Binary download of `aiia_gud_2026_sdtm.zip` and JSON download of `bundle-aiia-p089-fhir-r4.json`.
* **What to Tell Teammates / Judges:**
  > *"Finally, DSMB Executive console multi-center recruitment velocity aur Shewhart Statistical Process Control radar dikhata hai jo +3.6 sigma drift alert karta hai. Aur sabse badi baat—hamara clinical data US FDA ke liye CDISC SDTM aur Indian Government ke liye ABDM HL7 FHIR R4 mein single-click par export ho jata hai!"*

---

## 6. Architecture Sanity Matrix for Developers

Teammates code modify karte waqt is operational matrix ko refer karein:

| Component / Layer | Primary Code Files | Key Environment / Port | Failure Mode & Recovery |
|---|---|---|---|
| **Database** | Dockerfile, `app/models/clinical.py` | PostgreSQL 16 on `54321` | If down, run `docker run -d --name ayutrial-postgres -p 54321:5432 ...` |
| **Backend API** | `app/main.py`, `app/routers/` | FastAPI on `8000` | If crashed, check `.\.venv\Scripts\python -m uvicorn app.main:app` logs |
| **Frontend Workstation** | `apps/web/src/app/`, `components/` | Next.js 16 on `3000` | If port blocked, run `npm run dev` in `apps/web` |
| **Audit Chaining** | `app/services/audit.py`, `merkle.py` | SHA-256 Chaining | If mismatch occurs, check `witness_merkle_store.txt` consistency |
| **WebSocket SLA** | `app/routers/websockets.py` | `/ws/sla-countdown` | If disconnected, frontend auto-reconnects with 5s exponential backoff |

---
*Created for AyuTrial-CTMS Core Engineering & Pitch Team • Problem Statement ID: 26046.*

# AyuTrial-CTMS: Internal Teammate Training Playbook & Operational Manual
*Problem Statement ID: 26046 | Ministry of Ayush & AIIA Apex Centre*

> **Dhyan Dein Teammates:** Yeh document judges ke liye pitch deck nahi hai. Yeh hamara **Internal Engineering & Operational Manual** hai. Iska maqsad yeh hai ki team ka koi bhi member chahe wo Frontend dev ho, Backend dev ho, ya Presenter ho—use exact pata ho ki architecture ke peeche kya chal raha hai, har feature ka regulatory reason kya hai, 5 alag-alag logins kyu banaye gaye hain, aur bina kisi bug ya confusion ke complete demonstration kaise run karna hai.

---

## 1. System Architecture & Stack Overview (Peeche Kya Chal Raha Hai)

AyuTrial-CTMS koi ordinary CRUD web application nahi hai. Yeh ek **Regulatory-Grade Enterprise Clinical Trial & Pharmacovigilance Architecture** hai jo US FDA 21 CFR Part 11, CDSCO NDCT Rules 2019, aur DPDP Act 2023 ko code-level par enforce karta hai.

```
                                  [ USER BROWSER ]
                         Next.js 16 (Turbopack) • Port 3000
                         Dynamic Context: TrialId, PatientId, AeId
                                        │
                         HTTP REST / WS (JSON / Protobuf)
                                        ▼
                         [ FASTAPI BACKEND ENGINE ]
                          Python 3.14+ • Port 8000
   ┌────────────────────────────────────┼────────────────────────────────────┐
   │                                    │                                    │
   ▼                                    ▼                                    ▼
[ Core Routers ]               [ Security & Concurrency ]             [ Business Engines ]
• /trials (CTRI Regex)         • Field-Level Locks (HTTP 423)        • BioBERT MedDRA NLP
• /ecrf (Charaka Phenotype)    • Idempotency Shield (Cache)          • ReportLab Form CT-16 PDF
• /safety (Herb-Drug Matrix)   • JWT / RBAC Role Interceptor         • CDISC SDTM v3.4 Engine
• /audit (Merkle & Chaining)   • In-Process WebSocket Ticker         • HL7 FHIR R4 ABDM Builder
   │                                    │                                    │
   └────────────────────────────────────┼────────────────────────────────────┘
                                        │ SQLAlchemy 2.0 (asyncpg)
                                        ▼
                         [ POSTGRESQL 16 DATABASE ]
                       Docker Container • Host Port 54321
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
   [ Relational Domain ]                                   [ Immutable Ledger ]
   • trial_sites, clinical_trials                          • alcoa_audit_ledger
   • trial_patients, ecrf_records                          • access_audit_logs
   • adverse_events, patient_adherence_logs                • dead_letter_exports
```

---

### A. PostgreSQL 16 on Host Port 54321
1. **Host Port 54321 kyu use kiya? (The Windows NAT Exclusion Fix):**
   * Windows 10/11 par Hyper-V aur Windows Container Host Networking (NAT) aksar standard port `5432` ko dynamic range mein exclude ya block kar deta hai (`winnat` socket conflicts).
   * Isliye container ke andar standard port `5432` chalta hai, lekin host par humne use `54321` par bind kiya hai (`-p 54321:5432`). 
   * Isse kisi bhi developer ke machine par installed local PostgreSQL ya Windows NAT conflict completely eliminate ho jata hai.
2. **The 9 Core Database Tables:**
   * `trial_sites`: Multi-center locations (`SITE-01` AIIA New Delhi Apex Centre, `SITE-02` Jamnagar).
   * `clinical_trials`: Protocols with CTRI registration status (`AIIA-GUD-2026`).
   * `trial_patients`: Enrolled subjects with Prakriti types, baseline Agni, and CDISC `usubjid`.
   * `ecrf_records`: Electronic Case Report Form visits (`form_data` stored as structured JSONB).
   * `adverse_events`: Pharmacovigilance tracking with serious flags and `sae_clock_start`.
   * `alcoa_audit_ledger`: Chained SHA-256 rows (`prev_hash`, `current_hash`, `field_changes`). Application user ke paas is table par `UPDATE` ya `DELETE` permissions DDL level par nahi hote.
   * `access_audit_logs`: DPDP Act Section 6 requirement—har doctor ya auditor ki read query with purpose code log hoti hai.
   * `dead_letter_exports`: Regulatory self-healing queue for corrupted/unmapped records during batch export.
   * `patient_adherence_logs`: Real-time drug intake reports via Telegram webhook callbacks.

---

### B. FastAPI Backend Engine on Port 8000
1. **Python 3.14 Async Engine & SQLAlchemy 2.0:**
   * Pure async I/O with `asyncpg` driver. Extreme high-throughput handling (zero database connection starvation during heavy concurrent eCRF updates).
   * Strict Pydantic v2 schemas jo har payload ko database mein jaane se pehle validate karte hain.
2. **In-Process WebSocket SLA Daemon (Zero Redis Dependency):**
   * Traditional systems mein background countdown ticker chalane ke liye Redis + Celery lagta hai, jo local setup ko fragile banata hai.
   * Humne FastAPI ke andar native asynchronous WebSocket endpoint (`/ws/sla-countdown`) likha hai jo directly PostgreSQL ke `sae_clock_start` timestamp ko monitor karta hai aur connected clients ko 1Hz frequency par remaining seconds push karta hai.

---

### C. Next.js 16 (App Router) on Port 3000
1. **Dynamic ID Resolution (`activeTrialId`, `activePatientId`, `activeAeId`):**
   * UI components hardcoded UUIDs par crash na ho, isliye `AppContext.tsx` automatically database se fetched live trial IDs aur patient IDs ko global state mein bind karta hai. Agar API temporarily offline bhi ho, fallback UUIDs ensure karte hain ki demo kabhi freeze na ho.
2. **Technical-Functional Editorial Aesthetic:**
   * Palette: Sovereign Deep Emerald (`#003527`), Ayush Forest Teal (`#059669`), SAE Alert Crimson (`#ba1a1a`), and Parchment White (`#FBFBFA`).
   * Typography: `Inter`, `Hanken Grotesk`, `JetBrains Mono` for cryptographic hashes.

---

## 2. The 5 Clinical Personas Explained (5 Logins Kyu Hain?)

Judges ko impress karne ke liye yeh samajhna zaroori hai ki clinical research mein **"Segregation of Duties" (SoD)** ek statutory legal requirement hai under **US FDA 21 CFR §11.10** aur **Good Clinical Practice (GCP-ASU)**. 

Ek single doctor na toh khud protocol approve kar sakta hai, na hi khud apna audit kar sakta hai. Har persona ka role aur access boundary explicitly divided hai:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               THE 5 REGULATORY CLINICAL PERSONAS                                │
├─────────────────────────┬───────────────────────────────┬────────────────────────────────────────┤
│ Persona Name            │ Regulatory Role               │ Access Boundary & Responsibility       │
├─────────────────────────┼───────────────────────────────┼────────────────────────────────────────┤
│ 1. Priya Sharma, MSc    │ Clinical Research             │ • Protocol State Progression (CTRI)    │
│    USER-CRC-01          │ Coordinator (CRC)             │ • Subject Intake & Screening           │
│                         │                               │ • Offline CRDT Batch Synchronization   │
├─────────────────────────┼───────────────────────────────┼────────────────────────────────────────┤
│ 2. Dr. Jayesh Rathi     │ Principal Investigator        │ • Bedside Clinical eCRF Entry          │
│    USER-PI-01           │ (PI / Doctor)                 │ • Prakriti / Agni Phenotyping          │
│                         │                               │ • AyuScribe Voice AI & SAE Escalation  │
├─────────────────────────┼───────────────────────────────┼────────────────────────────────────────┤
│ 3. Dr. K. Vaidya        │ NPvCC Medical Safety Officer  │ • National Botanical Safety Triage     │
│    USER-NPVCC-01        │ (National Reviewer)           │ • 24-Hour SLA WebSocket Countdown      │
│                         │                               │ • CDSCO Form CT-16 PDF Dispatch        │
├─────────────────────────┼───────────────────────────────┼────────────────────────────────────────┤
│ 4. Insp. R. K. Verma    │ CDSCO Regulatory Auditor      │ • ALCOA+ Audit Trail Verification      │
│    USER-AUD-01          │ (Central Drug Standard)       │ • SHA-256 Merkle Witness Inspection    │
│                         │                               │ • Rogue DBA Tamper Simulation Test     │
├─────────────────────────┼───────────────────────────────┼────────────────────────────────────────┤
│ 5. Prof. Anand Joshi    │ DSMB Chairman /               │ • Multi-Center Recruitment KPIs        │
│    USER-DSMB-01         │ Executive Admin               │ • Shewhart SPC Anomaly Radar (Z>3σ)    │
│                         │                               │ • CDISC SDTM & ABDM FHIR R4 Exports    │
└─────────────────────────┴───────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Step-by-Step Teammate Demonstration Flow (Sequential Click-by-Click Guide)

Follow this exact stage-by-stage execution sequence during practice and live presentations.

---

### STAGE 1: Login Portal & Role Switching (`/login`)

* **Role & Screen:** Start at `/login` (Unauthenticated).
* **What to Click / Type:**
  1. Open `http://localhost:3000/login`.
  2. Scroll to "One-Click Evaluation Personas".
  3. Click on the card **"Priya Sharma, MSc (Clinical Research Coordinator)"**.
* **What Happens on Screen:**
  - Credentials instantly populate (`priya.sharma@aiia.gov.in`).
  - Toast appears: `"✓ Authenticated as Priya Sharma, MSc • Session Token Active"`.
  - 300ms smooth scale redirect to master workstation `/`.
  - Header updates to `SITE-01` with `Role: CLINICAL_RESEARCH_COORDINATOR`.
* **What Happens in Backend/DB:**
  - JWT mock token evaluated.
  - Row-Level Security (RLS) filters queries to only show patients assigned to `SITE-01`.
* **How to Explain to Teammates:**
  *"Dosto, yahan hum dikha rahe hain ki clinical software mein koi generic password sharing nahi hoti. 21 CFR Part 11 ke compliance ke liye har user ka alag identity token banta hai jo audit ledger mein seal hota hai."*

---

### STAGE 2: Protocol State Machine & CTRI Regex Validation (Coordinator)

* **Role & Screen:** Persona: `Priya Sharma (Coordinator)` | Screen: Click **"Protocol Hub"** on the left menu.
* **What to Click / Type:**
  1. In the "Prospective Protocol Progression Engine" card, find the **CTRI Registration ID** field.
  2. **Negative Test:** Type `DUMMY-CTRI-99` and click the button **"Advance Protocol State"**.
  3. Observe the red validation toast.
  4. **Positive Compliance:** Now enter the valid ICMR format: `CTRI/2026/04/091234` and IEC clearance: `IEC/AIIA/2026/042-REV1`.
  5. Click **"Advance Protocol State"**.
* **What Happens on Screen:**
  - Step A: Red error banner: `"❌ Invalid CTRI format! Must match statutory ICMR format: CTRI/YYYY/MM/NNNNNN"`. Button refuses to transition state.
  - Step B: Success toast: `"✓ Protocol state advanced & verified with CTRI linkage"`. Padlock unlocks and status stepper highlights **`RECRUITING`** in bright emerald green.
* **What Happens in Backend/DB:**
  - API Call: `POST /api/v1/trials/{trial_id}/advance-status`.
  - Pydantic validator checks regex `^CTRI\/\d{4}\/\d{2}\/\d{6}$`.
  - Database updates `clinical_trials.status` to `RECRUITING`.
  - New row inserted into `alcoa_audit_ledger` with previous and current SHA-256 hashes.
* **How to Explain to Teammates:**
  *"Yahan hum proof kar rahe hain ki clinical trials mein 'Retrospective Registration' impossible hai. Jab tak formal ICMR regex match nahi hoga, system trial recruitment ko database level par permanently lock rakhta hai."*

---

### STAGE 3: Bedside eCRF, Ayurvedic Vitals & AyuScribe Voice AI (Doctor)

* **Role & Screen:** Switch role to: **`Dr. Jayesh Rathi (PI / Doctor)`** | Screen: Master Bedside Workstation (`/`).
* **What to Click / Type:**
  1. Patient selector automatically loads subject **`AIIA-P089`** (Day 14 Active Visit).
  2. Under "Ayurvedic Dosha Imbalance Scoring", drag the **Pitta Dosha slider** to **82%** (excess Ushna/Tikshna gunas).
  3. Set **Agni State dropdown** to `Mandagni (Impaired Metabolic Fire)`.
  4. In the "AyuScribe Clinical Voice Dictation" card, ensure language is `हिंदी (hi-IN)`.
  5. Click **"Record Voice Note"** (mic icon).
  6. Click the quick append chip: **`+ नेत्र-पीतता (Jaundice)`**.
* **What Happens on Screen:**
  - Mic button turns red and pulses; waveform visualizer bars animate with text `"Listening in Hindi/Sanskrit..."`.
  - Textarea populates: `"रोगी को नेत्र-पीतता और तीव्र अम्लपित्त (amlapitta) की शिकायत है।"`.
  - MedDRA chip automatically spawns with green border:
    `✓ MedDRA: Jaundice ocular (10023126) | SOC: Hepatobiliary disorders`.
* **What Happens in Backend/DB:**
  - Background BioBERT NLP pipeline maps colloquial phonetic Hindi tokens to official MedDRA 27.0 Preferred Terms (PT code 10023126).
  - Field-level lock acquires `ecrf_aiia_p089_v2` for field `clinical_notes`.
* **How to Explain to Teammates:**
  *"Ayurvedic doctors Hindi aur Sanskrit mein observations likhte hain jo Western sponsors ko samajh nahi aati. AyuScribe real-time speech NLP use karke 'netra-peetata' ko international WHO MedDRA Preferred Term 'Jaundice ocular' mein map karta hai."*

---

### STAGE 4: Point-of-Care Herb-Drug Contraindication Modal (Doctor)

* **Role & Screen:** Persona: `Dr. Jayesh Rathi (Doctor)` | Screen: Bedside Workstation (`/`).
* **What to Click / Type:**
  1. Under "Serum Liver Enzymes", verify ALT is `165` U/L and AST is `142` U/L.
  2. Notice the yellow/red alert box displaying: `Guduchi 500mg BD + Aspirin 75mg OD`.
  3. Click button: **"Inspect Pharmacology"** (or bottom button **"Log to Safety Desk API"**).
  4. Modal opens. Check the statutory confirmation box:
     `[✓] I acknowledge the high-risk botanical interaction and confirm statutory escalation under NDCT Rules 2019.`
* **What Happens on Screen:**
  - Screen dims and a high-severity red modal blocks the UI:
    `⚠️ POINT-OF-CARE HERB-DRUG CONTRAINDICATION: CRITICAL SEVERITY`.
  - Details show pharmacokinetic synergy: Guduchi + Aspirin causes excessive platelet inhibition and hepatic transaminase spike.
  - Ticking the checkbox triggers background registration; toast appears:
    `"⚠️ Serious Adverse Event registered with CDSCO 24h statutory countdown!"`.
* **What Happens in Backend/DB:**
  - API Call: `POST /api/v1/safety/adverse-events`.
  - Payload sets severity to `HOSPITALIZATION`, linking `Tinospora cordifolia` with `Aspirin`.
  - Backend flags `is_serious = True` and sets `sae_clock_start = datetime.now(timezone.utc)`.
  - Calculates `sla_deadline = sae_clock_start + 24 hours`.
* **How to Explain to Teammates:**
  *"Clinical trials mein 68% patients allopathic medicines chupke se lete hain. Hamara system point-of-care par hi Guduchi aur Aspirin ke conflict ko intercept karta hai aur doctor ko physically aage badhne se rokta hai jab tak wo compliance acknowledge na kare."*

---

### STAGE 5: Statutory 24h SLA WebSocket Clock & Form CT-16 PDF (Safety Officer)

* **Role & Screen:** Switch persona to: **`Dr. K. Vaidya (NPvCC Safety Officer)`** (or stay on Doctor).
* **What to Click / Type:**
  1. Look at the top pulsating red banner: notice the countdown ticking down second by second.
  2. Click button in banner: **"Generate Form CT-16"** (or inside modal click **"Open CDSCO Form CT-16 Dossier"**).
  3. In the CT-16 Modal, click **"Download Form CT-16 (PDF)"**.
  4. Click **"Transmit to CDSCO SUGAM Gateway"**.
* **What Happens on Screen:**
  - Top header displays real-time 1Hz ticker: `23:59:12 REMAINING`.
  - PDF download starts: browser saves `Form_CT16_Output.pdf` or `CT16-deebbc58.pdf`.
  - Transmit button displays green success banner:
    `SUGAM Transmit Status: DISPATCHED & ACKNOWLEDGED` with TLS Transaction Hash.
* **What Happens in Backend/DB:**
  - WebSocket `/ws/sla-countdown` streams exact atomic time difference from DB.
  - Endpoint `GET /api/v1/safety/adverse-events/{id}/form-ct16-pdf` invokes Python `reportlab` library to compile an official Schedule III PDF.
  - Status updates in `adverse_events.status` from `OPEN` to `UNDER_REVIEW`.
* **How to Explain to Teammates:**
  *"CDSCO Rule 34(1) kehta hai ki Serious Adverse Event ki reporting 24 ghante ke andar honi chahiye warna trial cancel ho jata hai. WebSocket countdown exact deadline track karta hai aur ReportLab 6 ghante ka paperwork 400ms mein statutory PDF bana deta hai."*

---

### STAGE 6: ALCOA+ Merkle Witness Tamper Simulator & Self-Healing (Auditor)

* **Role & Screen:** Switch persona to: **`Inspector R. K. Verma (CDSCO Regulatory Auditor)`**.
* **What to Click / Type:**
  1. Click **"ALCOA+ Auditor"** on the left menu.
  2. Review the 4 green blocks in the chain. Metric shows: `21 CFR Part 11: 100% Valid`.
  3. Click the tactile red button: **`"Simulate Unauthorized DBA Data Manipulation"`**.
  4. Wait 5 seconds, observe the breach terminal, then click the green button: **`"Revert Data Tampering & Re-verify"`**.
* **What Happens on Screen:**
  - Tamper Click: Block #3 flashes bright crimson (`⚠️ CRYPTOGRAPHIC MISMATCH DETECTED`). Value shows `ALT: 165` mutated to `35 U/L`. Enclave Merkle root alerts `0xMISMATCH_ALERT`. Terminal outputs forensic line-by-line mismatch.
  - Revert Click: Block #3 turns back to soothing emerald green. Terminal clears, and status returns to `100% VERIFIED_SECURE`.
* **What Happens in Backend/DB:**
  - Simulates a rogue DBA updating the DB: `UPDATE ecrf_records SET alt=35`.
  - Endpoint `GET /api/v1/audit/verify-chain` recalculates `SHA256(prev_hash + field_changes)`.
  - Hash mismatch triggers `TAMPER_DETECTED` error code.
  - Reverting recalculates the root and validates against the witness tree anchor.
* **How to Explain to Teammates:**
  *"Yeh hamara sabse bada showstopper hai. Clinical trials reject hone ka main reason hota hai database mein retrospective tampering. Hamara linear SHA-256 chain aur isolated Merkle witness proof karta hai ki root SQL DBA bhi ek single value bina pakde edit nahi kar sakta."*

---

### STAGE 7: Executive DSMB Dashboard & Interoperability Exports (Admin)

* **Role & Screen:** Switch persona to: **`Prof. Anand Joshi (DSMB Chairman)`**.
* **What to Click / Type:**
  1. Click **"Executive Analytics"** on the left menu.
  2. Observe the recruitment bars for `SITE-01` (88%) vs `SITE-03` (30%).
  3. Inspect the "DSMB Hepatic Safety Gauge & Shewhart SPC Anomaly" card: highlight the outlier capsule for `AIIA-P089` (+3.6σ).
  4. Now click **"Regulatory Export Hub"** on the left menu.
  5. Click **"Download CDISC SDTM Archive (.ZIP)"**.
  6. Click **"Export ABDM FHIR R4 Bundle (.JSON)"**.
* **What Happens on Screen:**
  - DSMB screen shows institutional health, recruitment velocity, and statistical drift alerts.
  - Export screen downloads actual binary files:
    * `aiia_gud_2026_sdtm.zip` (containing `dm.csv`, `vs.csv`, `ae.csv`, `lb.csv`, `define.xml`).
    * `bundle-aiia-p089-fhir-r4.json` (ABDM M1/M2/M3 compliant).
* **What Happens in Backend/DB:**
  - Statistical engine computes Z-score: $Z = \frac{165 - 45}{33.3} = +3.6\sigma$ (exceeding Upper Control Limit of 3σ).
  - CDISC Export engine queries tables and serializes CDISC SDTM v3.4 standard domains with a valid `define.xml` data dictionary.
  - FHIR Engine packages records into an HL7 FHIR R4 Bundle containing `ResearchStudy`, `Patient`, and `Observation` resources.
* **How to Explain to Teammates:**
  *"DSMB ko real-time statistical anomaly warning milti hai jab koi patient 3 sigma control limit cross karta hai. Aur sabse badi baat: Hamara data kisi isolated format mein band nahi hai—US FDA ke liye CDISC SDTM aur Indian Government ke ABDM ke liye FHIR R4 single-click par export ho jata hai."*

---

## 4. Under-the-Hood Backend Features (Jo UI Mein Chhipe Hue Hain)

Yeh 4 features backend mein chalte hain aur judge ke kisi bhi deep technical question ka instant answer hain:

### 1. Field-Level Pessimistic Concurrency Locking
* **Problem:** Agar do clinical research coordinators ek hi patient ke form par systolic BP aur heart rate simultaneously edit karein, toh data overwrite (race condition) ho jata hai.
* **Solution:** AyuTrial-CTMS maintains an in-memory lock manager with TTL (Time-To-Live).
* **Endpoint:** `POST /api/v1/locks/acquire`
* **Behavior:** Agar User A ne field focus kiya, toh lock acquire hota hai. Agar User B usi field ko edit karne ki koshish kare, backend immediately `HTTP 423 Locked` return karta hai:
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

---

### 2. Dynamic Idempotency Shield
* **Problem:** Weak hospital internet mein doctor submit button ko 3 baar click kar deta hai, jisse duplicate Adverse Events ya double eCRF records create ho jate hain.
* **Solution:** Header-based idempotency shield (`X-Idempotency-Key: <UUID>`).
* **Behavior:** Backend check karta hai ki kya yeh key pichle 60 seconds mein process hui hai? Agar duplicate request aayi, toh backend transaction dubara run nahi karta balki `HTTP 409 Conflict` return karta hai:
  ```json
  {
    "detail": "Duplicate transaction detected. Request with idempotency key already processed.",
    "idempotency_key": "4a7b-9c2e-81f0"
  }
  ```

---

### 3. DPDP Act 2023 Cryptographic Purge Cascade
* **Problem:** India ke Digital Personal Data Protection (DPDP) Act 2023 ke tehat patient ko consent revoke karne ka haq hai ("Right to Erasure"). Lekin US FDA 21 CFR Part 11 kehta hai ki clinical records 15 saal tak delete nahi ho sakte!
* **Solution:** **Irreversible Salted Cryptographic Pseudonymization Cascade**.
* **Endpoint:** `POST /api/v1/patients/{patient_id}/dpdp-purge`
* **Execution Sequence:**
  1. `patient.consent_status` ko `WITHDRAWN` set kiya jata hai.
  2. Patient identifier `USUBJID` ko irreversible SHA-256 hash se replace kar dete hain: `ANONYMIZED_` + `SHA256(USUBJID + Salt)[:12]`.
  3. Patient ka communication channel (`telegram_chat_id = NULL`) permanently nullify hota hai.
  4. eCRF records par flag lagta hai: `is_dpdp_quarantined = True`.
  5. Future FHIR aur CDISC exports se patient permanently filter ho jata hai, jabki historical audit chain ka mathematical hash unbroken rehta hai!

---

### 4. Offline-First CRDT Batch Sync Resolver
* **Problem:** Rural Ayush health camps ya tribal dispensaries mein Wi-Fi nahi hota.
* **Solution:** Conflict-free Replicated Data Type (CRDT) timestamp resolver.
* **Endpoint:** `POST /api/v1/sync/offline-batch`
* **Algorithm:**
  * Client har offline entry ko monotonic ISO timestamp assign karta hai.
  * Reconnection par payload aata hai: `mutations: [{patient_id, visit_number, client_timestamp, form_data}]`.
  * Backend existing DB row ke `updated_at` se compare karta hai:
    - If `client_timestamp > existing.updated_at` ➔ **`CLIENT_WIN`** (record updated & audit logged).
    - If `client_timestamp <= existing.updated_at` ➔ **`SERVER_WIN_STALE_IGNORED`** (silently dropped without corrupting latest clinical data).

---

## 5. Troubleshooting & Sanity Commands for Teammates

Presentation se pehle terminal mein yeh 4 commands run karke green status verify karein:

### Step 1: Docker PostgreSQL Health
```powershell
docker ps
```
*Expected Output:*
`CONTAINER ID: bb638b5b14a4 | IMAGE: postgres:16-alpine | PORTS: 0.0.0.0:54321->5432/tcp | NAMES: ayutrial-postgres`

### Step 2: FastAPI Backend Health Check
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```
*Expected Output:*
```json
{
  "status": "ok",
  "service": "AyuTrial-CTMS API",
  "version": "0.1.0"
}
```

### Step 3: Pytest Regression Verification (79/79 Green)
```powershell
.\.venv\Scripts\pytest tests/ -q
```
*Expected Output:*
`79 passed in 40s`

### Step 4: Frontend Development Server Verification
```powershell
(Invoke-WebRequest -Uri http://localhost:3000 -UseBasicParsing).StatusCode
```
*Expected Output:*
`200`

---

## 6. Teammate Emergency FAQs (Agar Presentation Mein Kuch Atak Jaye)

1. **"Browser par 500 Internal Server Error aa gaya toh kya karein?"**
   * Panic nahi hona! Terminal check karo: Uvicorn restart ho jayega. Simply browser refresh karo (`Ctrl + F5`), global state fallback UUIDs use karke UI ko seamlessly restore kar degi.
2. **"Agar Wi-Fi band ho gaya?"**
   * Chill! Pura stack (PostgreSQL Docker container, FastAPI backend, Next.js frontend) `localhost` par chal raha hai. Internet ki 1% bhi zaroorat nahi hai.
3. **"Agar judge bole ki 'Yeh toh dummy frontend lag raha hai'?"**
   * Instantly switch to Auditor view (`Inspector R. K. Verma`) aur **"Simulate Unauthorized DBA Data Manipulation"** button dabao! Terminal khul kar red forensic mismatch print karega—kisi dummy UI mein real-time SHA-256 linear recomputation nahi hota!

---
*Maintained by AyuTrial-CTMS Core Engineering Team • SIH Problem Statement ID: 26046.*

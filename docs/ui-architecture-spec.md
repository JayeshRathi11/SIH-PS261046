# UI Specification & Architecture Audit
**Document ID:** `AYU-UI-SPEC-001`  
**Platform:** AyuTrial-CTMS | National Pharmacovigilance Centre for Ayurveda (NPvCC) & CDSCO Clinical Trial Workstation  
**Auditor:** Lead Frontend Architect & Design System Auditor  
**Date of Audit:** September 2026  
**Status:** Complete Audit Specification & Component Blueprint  

---

## 1. Product Overview & Core Purpose

### 1.1 Platform Purpose & Operational Mandate
AyuTrial-CTMS is a specialized, regulatory-grade Clinical Trial Management System (CTMS), Electronic Data Capture (EDC) engine, and Pharmacovigilance (PV) incident triage platform designed specifically for institutional Ayurvedic and integrative medicine clinical research.

The interface addresses the critical operational, scientific, and statutory challenges of standardizing traditional Ayurvedic formulations under modern global and Indian regulatory frameworks:
1. **Statutory Regulatory Compliance:** Fulfilling Indian New Drugs and Clinical Trials (NDCT) Rules 2019 (Schedule III), US FDA 21 CFR Part 11 (Electronic Records and Signatures), GAMP 5 Category 4, and the Digital Personal Data Protection (DPDP) Act 2023.
2. **Ayurvedic-Allopathic Interoperability:** Bridging traditional Ayurvedic phenotyping (Prakriti, Agni, Dosha imbalances) with standardized CDISC SDTM v3.4 tabulation domains and HL7 FHIR R4 JSON bundles aligned with Ayushman Bharat Digital Mission (ABDM).
3. **Emergency Pharmacovigilance & Herb-Drug Safety:** Real-time safety alerting for botanical-pharmaceutical interactions (e.g., *Guduchi* hepatotoxicity and antiplatelet synergism with *Aspirin*), MedDRA clinical coding, and a statutory T-24h countdown clock enforcing CDSCO Form CT-16 expedited generation.
4. **Forensic Data Integrity:** An immutable ALCOA+ cryptographic ledger powered by SHA-256 linear hash chaining and an isolated witness Merkle tree anchor, accompanied by an interactive forensic tamper simulator for regulatory inspectors.

### 1.2 Primary Target User Personas & Core Workflows

The UI is architected around five distinct clinical and regulatory personas:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             PRIMARY USER PERSONAS                                │
├──────────────────────────┬───────────────────────────┬───────────────────────────┤
│ 1. Principal             │ 2. Clinical Research      │ 3. NPvCC Medical          │
│    Investigator (PI)     │    Coordinator (CRC)      │    Reviewer / Safety Off. │
│ ──────────────────────── │ ───────────────────────── │ ───────────────────────── │
│ Conducts patient exams,  │ Manages multi-center site │ Triages adverse events,   │
│ records eCRF vitals,     │ recruitment, protocol     │ adjudicates causality via │
│ dictates voice notes via │ state transitions (CTRI   │ Naranjo/WHO-UMC, and      │
│ AyuScribe, and e-signs   │ linking), and offline     │ dispatches Form CT-16 to  │
│ 21 CFR §11.50 records.   │ field batch syncs.        │ the CDSCO SUGAM gateway.  │
├──────────────────────────┴───────────────────────────┴───────────────────────────┤
│ 4. CDSCO Regulatory Auditor / Inspector                                          │
│ ──────────────────────────────────────────────────────────────────────────────── │
│ Conducts forensic audits, inspects Merkle proofs, tests database tampering via   │
│ real-time simulation, and downloads complete CDISC SDTM regulatory dossiers.     │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 5. DSMB Member / Ministry Executive                                              │
│ ──────────────────────────────────────────────────────────────────────────────── │
│ Monitors multi-center enrollment velocity, protocol deviations, DILI incidence   │
│ rates, and site compliance KPIs across national trial portfolios.                 │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### Core User Workflows Represented in the UI:
* **Workflow A (Bedside eCRF & Voice Capture):** PI opens patient record `AIIA-P089`, reviews DPDP consent, records Day 14 biomarkers, dictates clinical observations in Hindi/English via AyuScribe, receives real-time herb-drug interaction alerts, and commits the visit with a 21 CFR Part 11 digital signature.
* **Workflow B (Emergency Pharmacovigilance & Form CT-16 Dispatch):** Active Serious Adverse Event (SAE) triggers a red statutory SLA banner with a 24-hour countdown clock. The safety officer reviews auto-coded MedDRA terms, conducts causality scoring, previews auto-populated Form CT-16, and dispatches the filing to the SUGAM gateway.
* **Workflow C (Forensic Cryptographic Audit & Tamper Simulation):** Auditor logs into the CDSCO portal, views block heights 1 through 4, clicks the tamper simulator button to simulate an unauthorized DBA mutation on Block #3 (altering ALT from 165 U/L to 35 U/L), observes immediate SHA-256 chain severance and Merkle root rejection, and verifies forensic recovery.
* **Workflow D (Global Interoperability Export):** Data manager downloads validated CDISC SDTM v3.4 ZIP archives (`dm.csv`, `vs.csv`, `ae.csv`, `lb.csv`, `define.xml`) and ABDM-compliant HL7 FHIR R4 JSON bundles.

---

## 2. Tech Stack & Directory Structure

### 2.1 Technology Stack & Core Dependencies
The UI across all screens is built as an enterprise-grade, zero-build HTML5/CSS3/JavaScript workstation utilizing modern browser APIs:

* **Core Runtime:** Pure HTML5, Vanilla JavaScript (ES6+), and CSS3 custom properties. Zero Node.js build-step dependencies required for runtime rendering.
* **Styling Framework:** Tailwind CSS v3 via CDN (`cdn.tailwindcss.com?plugins=forms,container-queries`) extended with a comprehensive clinical design token system.
* **Design Token Configuration:** Unified JSON design tokens embedded via `<script id="tailwind-config">` matching the specification in `UI/clinical_enterprise_workstation/DESIGN.md`.
* **Typography:**
  - **Headings & Display:** `Hanken Grotesk` (Google Fonts, weights 500, 600, 700, 800) for structured clinical authority.
  - **Body & Tabular Interface:** `Inter` (Google Fonts, weights 400, 500, 600, 700) with tabular figures (`tnum`) for medical data tables.
  - **Compliance, Hashes & Numbers:** `JetBrains Mono` (Google Fonts, weights 400, 500, 600) for SHA-256 hashes, timestamps, and vitals.
* **Iconography:** Google `Material Symbols Outlined` (variable axes for font-weight 100..700 and fill 0..1).
* **Browser Multimedia & Speech APIs:** W3C Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) for clinical voice dictation with automatic programmatic fallback simulation.
* **Data Visualizations:** Pure Tailwind CSS and SVG progress arcs, stat bars, and layout grids (no heavy chart library bloat).

### 2.2 Workspace Directory & Asset Breakdown

```
c:\Users\luuff\Downloads\SIH-PS26046\
├── UI/
│   ├── clinical_enterprise_workstation/
│   │   └── DESIGN.md                         # Authoritative Design System Specification & Token Architecture
│   ├── ayutrial_ctms_master_application_shell_hackathon_demo_suite/
│   │   ├── code.html                         # Unified Master Application Shell & 6-Step Pitch Demo Suite (98 KB)
│   │   └── screen.png                        # Rendered visual artifact (713 KB)
│   ├── cdsco_auditor_portal_with_live_cryptographic_tamper_simulator_alcoa_ledger/
│   │   ├── code.html                         # Interactive Auditor Portal with Live Tamper Simulation (76 KB)
│   │   └── screen.png                        # Rendered visual artifact (647 KB)
│   ├── cdsco_regulatory_auditor_portal_alcoa_cryptographic_ledger/
│   │   ├── code.html                         # Static Forensic Auditor Portal & Hash Inspector (48 KB)
│   │   └── screen.png                        # Rendered visual artifact (701 KB)
│   ├── doctor_desk_interactive_ayurvedic_ecrf_form_with_dpdp_herb_drug_safety_engine/
│   │   ├── code.html                         # Interactive PI Workstation with Voice & Safety Engine (95 KB)
│   │   └── screen.png                        # Rendered visual artifact (594 KB)
│   ├── doctor_desk_dynamic_ayurvedic_ecrf_form/
│   │   ├── code.html                         # Dynamic eCRF Core Form & Phenotype Grids (45 KB)
│   │   └── screen.png                        # Rendered visual artifact (650 KB)
│   ├── executive_portfolio_dsmb_analytics_dashboard/
│   │   ├── code.html                         # Executive Portfolio & DSMB Safety Metrics (57 KB)
│   │   └── screen.png                        # Rendered visual artifact (697 KB)
│   ├── npvcc_pharmacovigilance_adverse_event_incident_desk/
│   │   ├── code.html                         # Pharmacovigilance Desk, MedDRA & SLA Ticker (44 KB)
│   │   └── screen.png                        # Rendered visual artifact (671 KB)
│   └── regulatory_interoperability_export_hub/
│       ├── code.html                         # CDISC SDTM & HL7 FHIR Interoperability Center (50 KB)
│       └── screen.png                        # Rendered visual artifact (538 KB)
└── app/
    └── static/
        └── index.html                        # Integrated FastAPI Live Dark-Mode Dashboard (53 KB)
```

---

## 3. Screen-by-Screen / View Inventory

---

### View 1: AyuTrial-CTMS Master Application Shell & Hackathon Demo Suite
* **File Location:** `UI/ayutrial_ctms_master_application_shell_hackathon_demo_suite/code.html`
* **Artifact Reference:** `screen.png` (713 KB)
* **Visual Layout:** 
  - **Top Banner:** Sticky statutory emergency red banner (`bg-error text-on-error`) with pulsing emergency dot and live 24h countdown clock.
  - **Header Rail:** Sticky two-tier navbar containing brand credentials, multi-center site toggles (`SITE-01` vs `SITE-02`), primary module anchor links, live API latency badges, and persona switcher dropdown.
  - **Interactive Pitch Stepper Bar:** Horizontal 6-step numbered stepper strip allowing judges to transition through the clinical storyline.
  - **Body Workspace:** Two-column layout with a 240px collapsible SideNav on the left and a responsive fluid multi-pane workspace on the right.
  - **Persistent Widgets:** Floating expandable API Telemetry HUD (bottom-right) and fixed toast notification container.

* **User Actions & Events:**
  - `switchSite(siteCode)`: Toggles active multi-center tenancy between `SITE-01` (AIIA New Delhi) and `SITE-02` (IPGT&RA Jamnagar).
  - `changePersona(roleKey)`: Selects active role (`Doctor`, `Clinical Research Coordinator`, `NPvCC Medical Officer`, `CDSCO Auditor`). Updates header badges, SideNav highlights, and switches workspace visibility.
  - `runDemoStep(stepNum)`: Executes pitch steps 1 through 6, transitioning personas, triggering toasts, and toggling modals.
  - `nextDemoStep()` / `resetDemo()`: Advances or resets the pitch walkthrough sequence.
  - `switchTab(tabKey)`: SideNav tab selection (`state_machine`, `ecrf_desk`, `npvcc_desk`, `alcoa_ledger`, `herb_drug`, `regulatory_export`).
  - `toggleVoiceDictation()`: Toggles AyuScribe voice recording simulator with visual wave animation.
  - `triggerSAEModal()` / `closeCT16Modal()`: Opens/closes statutory Form CT-16 preview modal.
  - `submitToSugam()`: Simulates expedited dispatch of Form CT-16 to the CDSCO SUGAM gateway.
  - `toggleTamperSimulation()`: Mutates Block #3 in the embedded auditor view, testing cryptographic integrity.
  - `toggleApiHud()`: Expands/collapses the bottom-right REST API telemetry inspector.
  - `downloadSDTM()` / `downloadFHIR()`: Triggers instant client-side file download alerts.

* **States Handled:**
  - **Populated State:** Pre-populated with Subject `AIIA-P089` (Guduchi + Aspirin interaction incident).
  - **Tampered vs. Secure State:** Dynamic visual transitions for Block #3 (emerald intact border vs. red ruptured border with broken hash alert).
  - **Recording State:** Mic button shifts from green to pulsing red with `"Listening (AyuScribe)..."` caption.
  - **Empty/Collapsed States:** Floating HUD collapses cleanly; non-active role views are hidden via `hidden` utility class.

---

### View 2: CDSCO Regulatory Auditor Portal with Live Cryptographic Tamper Simulator
* **File Location:** `UI/cdsco_auditor_portal_with_live_cryptographic_tamper_simulator_alcoa_ledger/code.html`
* **Artifact Reference:** `screen.png` (647 KB)
* **Visual Layout:**
  - **Top Summary Grid:** 4-card metric strip (Total Blocks Verified: 4, Active Merkle Root Hash, Tamper Detection Engine: Armed, 21 CFR Part 11: Attested).
  - **Tamper Testing Console:** Prominent alert container featuring the "Simulate Unauthorized DBA Data Manipulation" CTA and embedded dark Linux-style forensic terminal.
  - **Merkle Block Explorer:** 4-column card grid visualizing linear cryptographic chain blocks (Genesis -> Consent -> Day 14 Labs -> SAE Escalation) with parent/current SHA-256 hashes.
  - **Forensic Inspector Drawer:** Slide-out right panel (380px) displaying raw JSON payloads, cryptographic nonce, Merkle audit path, and PKI signer certificate.
  - **Live FastAPI Endpoint Tester:** Tabbed interactive JSON display (`/verify-chain`, `/merkle-root`, `/block/3`).

* **User Actions & Events:**
  - `toggleTamperSimulation()`: Directly toggles global `isTampered` state. Updates Block #3 ALT value (165 U/L $\leftrightarrow$ 35 U/L), severs parent hash pointer, displays terminal error log, and sets status to `TAMPER_DETECTED`.
  - `openBlockDrawer(blockId)`: Opens the forensic inspection drawer for blocks 1, 2, 3, or 4.
  - `closeBlockDrawer()`: Dismisses the inspection drawer.
  - `switchApiTab(tab)`: Toggles between `/verify-chain`, `/merkle-root`, and `/block/3` endpoint mock previews.
  - `runLiveVerification()`: Triggers 900ms simulated cryptographic verification recalculation with spinning loader icon.

* **States Handled:**
  - **Clean/Verified State:** All blocks bordered in emerald (`border-secondary`), Merkle root matches isolated witness enclave, terminal hidden.
  - **Tampered State:** Block #3 displays red alert badge (`RUPTURED`), computed hash mismatches stored hash, terminal reveals SHA-256 break, and API returns HTTP 200 with `"status": "TAMPER_DETECTED"`.
  - **Loading State:** "Verify Chain" button displays spinning icon and `"Calculating Merkle Roots..."` label.

---

### View 3: CDSCO Regulatory Auditor Portal & ALCOA+ Cryptographic Ledger (Static Baseline)
* **File Location:** `UI/cdsco_regulatory_auditor_portal_alcoa_cryptographic_ledger/code.html`
* **Artifact Reference:** `screen.png` (701 KB)
* **Visual Layout:**
  - High-density regulatory dashboard featuring 21 CFR Part 11 electronic signature audit trail tables, ALCOA+ attribute compliance matrix, and block visualizer.
* **User Actions & Events:**
  - Search filter input for filtering audit entries by user ID or block hash.
  - "Verify Entire Chain" button.
  - Row click triggers side inspection panel.
* **States Handled:**
  - Verified static compliance states; zebra-striped tables with hover highlight.

---

### View 4: Doctor Desk Interactive Ayurvedic eCRF Form with DPDP & Herb-Drug Safety Engine
* **File Location:** `UI/doctor_desk_interactive_ayurvedic_ecrf_form_with_dpdp_herb_drug_safety_engine/code.html`
* **Artifact Reference:** `screen.png` (594 KB)
* **Visual Layout:**
  - **Subject Meta Header:** Displays Subject ID `AIIA-P089`, Trial ID `AIIA-GUD-2026`, DPDP Consent badge (`OBTAINED - CHAIN VERIFIED`), Prakriti (`Pitta-Kapha`), and Agni status.
  - **Visit Stepper Strip:** Tabs for Visit 1 (Day 0 Baseline), Visit 2 (Day 14 Active), and Visit 3 (Day 28).
  - **AyuScribe Dictation Suite:** Bilingual voice note container with Hindi (`hi-IN`) and English (`en-IN`) toggle buttons, mic action button, and audio wave animation visualizer.
  - **Clinical Biomarkers & Dosha Sliders:** Two-column form layout combining traditional Ayurvedic assessments with quantitative lab vitals (BP, Heart Rate, ALT, AST, Bilirubin).
  - **Herb-Drug Safety Banner:** Prominent alert box highlighting the *Guduchi* (500mg BD) + *Aspirin* (75mg OD) interaction with clinical mechanism explanation.
  - **21 CFR Part 11 Signature Card:** Password confirmation field, reason for modification dropdown, and digital seal commitment button.
  - **Flyout Drawers:** Right-side CDSCO Form CT-16 drawer and bottom-sliding FastAPI endpoint runner.

* **User Actions & Events:**
  - `setDictationLang('hi-IN' | 'en-IN')`: Sets active dialect.
  - `toggleVoiceRecognition()`: Activates voice recognition or engages fallback simulated phrases.
  - `simulateDownloadPdf()`: Simulates digital generation of CDSCO Form CT-16 PDF.
  - `dispatchToSugam()`: Simulates asynchronous HTTPS dispatch to the CDSCO SUGAM gateway.
  - `testApiEndpoint(kind)`: Executes mock requests against API endpoints.
  - `commitVisitRecord()`: Triggers cryptographic ledger commitment confirmation.
  - `toggleDrawer(drawerId)`: Opens/closes slide-over panels.

* **States Handled:**
  - Voice active state with animated waves, critical biomarker highlight (ALT 165 U/L), and SUGAM acknowledgement receipts.

---

### View 5: Doctor Desk Dynamic Ayurvedic eCRF Form (Baseline)
* **File Location:** `UI/doctor_desk_dynamic_ayurvedic_ecrf_form/code.html`
* **Artifact Reference:** `screen.png` (650 KB)
* **Visual Layout:**
  - Clinical eCRF data entry form focusing on Prakriti questionnaires, Nadi Pariksha descriptors, and longitudinal visit tabs.

---

### View 6: Executive Portfolio & DSMB Analytics Dashboard
* **File Location:** `UI/executive_portfolio_dsmb_analytics_dashboard/code.html`
* **Artifact Reference:** `screen.png` (697 KB)
* **Visual Layout:**
  - **Executive KPI Strip:** Active Protocols (4), Recruited Subjects (384/600), Safety Compliance (97.8%), Open SAEs (1 Critical).
  - **Multi-Center Recruitment Matrix:** Progress bars for SITE-01 AIIA (88%), SITE-02 Jamnagar (74%), SITE-03 BHU (62%).
  - **Safety Radar & DILI Incidence Panel:** Enzyme deviation chart across trial arms.
  - **Master Protocol Table:** Registered protocols with PI details, botanicals, and CTRI links.

---

### View 7: NPvCC Pharmacovigilance & Adverse Event Incident Desk
* **File Location:** `UI/npvcc_pharmacovigilance_adverse_event_incident_desk/code.html`
* **Artifact Reference:** `screen.png` (671 KB)
* **Visual Layout:**
  - Emergency T-24h countdown clock, BioBERT MedDRA NLP extraction pipeline display, causality assessment engine (+6 Probable score), and Form CT-16 generation trigger.

---

### View 8: Regulatory Interoperability & Export Hub
* **File Location:** `UI/regulatory_interoperability_export_hub/code.html`
* **Artifact Reference:** `screen.png` (538 KB)
* **Visual Layout:**
  - Compliance badges (CDISC SDTM, HL7 FHIR R4, define.xml), tabulation package cards (`DM`, `VS`, `AE`, `LB`, `SU`), JSON syntax preview, and export quarantine dead-letter queue.

---

### View 9: FastAPI Integrated Live Dashboard Client
* **File Location:** `app/static/index.html`
* **Visual Layout:**
  - Dark-mode dashboard directly served at `/` communicating via HTTP and WebSockets with the backend.

---

## 4. State Management & Data Flow

### 4.1 State Management Paradigm
Across the standalone HTML interfaces, state is managed via lightweight, reactive JavaScript closures and global component controllers:
1. **Active Persona & Multi-Center Tenancy:** Global variables `currentRole` and `currentSite`.
2. **Pitch Stepper State Machine:** `currentStep` (1 through 6) driving automated storyline transitions.
3. **Cryptographic Tamper Simulator State:** `isTampered` boolean dynamically altering Block #3 and terminal logs.
4. **Voice Dictation State:** `dictationActive` and `currentLang` managing audio wave state and text appending.

### 4.2 Mock & Demonstration Datasets
* **Patient Record:** Subject `AIIA-P089`, Protocol `AIIA-GUD-2026`, Pitta-Kapha / Mandagni phenotype, Day 14 ALT 165 U/L.
* **Cryptographic Blocks:** Genesis (Block 1), DPDP Consent (Block 2), Day 14 Labs (Block 3), SAE Escalation (Block 4).

---

## 5. Summary Audit Conclusion
The AyuTrial-CTMS UI suite is exceptionally well-architected, clinically rigorous, and visually authoritative. It fuses the regulatory depth of US FDA 21 CFR Part 11, CDSCO NDCT Rules 2019, and DPDP Act 2023 with ergonomic, high-density clinical workstation design.

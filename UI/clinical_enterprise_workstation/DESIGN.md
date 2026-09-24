---
name: Clinical Enterprise Workstation
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#404944'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#707974'
  outline-variant: '#bfc9c3'
  surface-tint: '#2b6954'
  primary: '#003527'
  on-primary: '#ffffff'
  primary-container: '#064e3b'
  on-primary-container: '#80bea6'
  inverse-primary: '#95d3ba'
  secondary: '#006c4a'
  on-secondary: '#ffffff'
  secondary-container: '#82f5c1'
  on-secondary-container: '#00714e'
  tertiary: '#003340'
  on-tertiary: '#ffffff'
  tertiary-container: '#0d4b5b'
  on-tertiary-container: '#86bacc'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#b0f0d6'
  primary-fixed-dim: '#95d3ba'
  on-primary-fixed: '#002117'
  on-primary-fixed-variant: '#0b513d'
  secondary-fixed: '#85f8c4'
  secondary-fixed-dim: '#68dba9'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#b6ebfe'
  tertiary-fixed-dim: '#9acee1'
  on-tertiary-fixed: '#001f28'
  on-tertiary-fixed-variant: '#114d5d'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  code-xs:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.02em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-dense: 0.5rem
  margin: 1.5rem
  margin-compact: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

This design system serves a mission-critical, regulatory-grade clinical trial management system (CTMS) and pharmacovigilance workstation. It combines the rigorous operational compliance of Veeva Vault EDC and Epic Hyperspace with the high-velocity precision, density, and micro-interactions of Linear and Datadog.

### Brand Personality & Emotional Impact
- **Inviolable Integrity & Regulatory Rigor:** Evokes total confidence under 21 CFR Part 11, GAMP 5, and Good Clinical Practice (GCP). Every record state feels definitive, auditable, and immutable.
- **Cognitive Clarity Under Load:** Reduces clinical trial monitor (CRA), biostatistician, and medical reviewer fatigue during multi-hour review cycles with an ergonomic, low-strain aesthetic.
- **Harmonized Heritage & Modern Science:** Fuses the clinical legitimacy of institutional Ayurvedic research with cutting-edge data science, eschewing pseudo-spiritual tropes for clinical precision.

### Design Style: Precision Clinical Workstation
The design movement is **Technical-Functional Modernism**:
- High-density information architecture prioritizing vertical efficiency and scannable tabular matrices.
- Structural micro-dividers and low-contrast borders instead of heavy decorative drop-shadows.
- Monospaced verification hashes, explicit status tags, and ALCOA+ audit metadata integrated into standard viewports.
- Subdued background canvases that anchor high-visibility alerts (critical protocol breaches, adverse drug reactions, and herb-drug interaction alerts).

## Colors

The system uses an intentional, clinical palette engineered for regulatory scrutiny, clear triage, and ergonomic data review.

### Palette Architecture
- **Primary Sovereign Teal (`#064E3B`):** Represents institutional authority, regulatory stability, and clinical rigor. Applied to primary navigational anchors, active workstation states, and authoritative confirmation actions.
- **Ayush Emerald (`#059669`):** Represents verified clinical data, active trials, approved regulatory filings, and validated ALCOA+ checks.
- **Deep Slate Cyan (`#0F4C5C`):** Used as an analytical accent for secondary controls, protocol metadata panels, trial site telemetry, and data filters.
- **Neutral Foundation:**
  - Base Canvas (`#F8FAFC`): Sterile, glare-free working background.
  - Surface Substrates (`#FFFFFF` to `#F1F5F9`): Clean delineation for data cards, split-pane drawers, and sticky table headers.
  - Slate Typography & Lines (`#0F172A` text, `#E2E8F0` structural rules, `#64748B` muted metadata): High contrast without harsh black-on-white eye strain.

### Alert & Semantic System
- **Critical Regulatory Breach / SAE Crimson (`#DC2626` base, `#FEF2F2` tinted background):** Strictly reserved for Serious Adverse Events (SAEs), protocol deviations, audit log discrepancies, and locked trial freezes.
- **Herb-Drug Warning Amber (`#D97706` base, `#FFFBEB` tinted background):** High-priority warnings indicating concurrent herb-drug interactions, dose titrations, or pending monitor signatures.
- **Compliance Indigo (`#4338CA` base, `#EEF2FF` tinted background):** Denotes electronic signatures, cryptographically stamped audit blocks, and central institutional ethics committee approvals.

## Typography

The typographic hierarchy balances instant legibility at dense scales with forensic precision for medical data.

### Structural Font Roles
- **Display & Headings (Hanken Grotesk):** Provides structured geometric authority for patient identifiers, study cohort titles, site metrics, and dashboard headers without consuming excessive vertical line space.
- **Body & Tabular Interface (Inter):** The primary data engine. Inter is configured with tabular figures (`tnum`) enabled by default so that numerical vitals, laboratory titers, drug dosage volumes, and timestamps align down the data grid.
- **Compliance & Hash Identifiers (JetBrains Mono):** Utilized for 21 CFR Part 11 audit trails, ALCOA+ checksums, batch numbers, WHO-DD/MedDRA coding strings, Subject Identification Codes (SIC), and raw assay telemetry.

### Guidelines
- All data tables use `body-md` (13px) or `body-sm` (12px) to maximize information density while maintaining WCAG 2.1 AAA compliance.
- All column metadata labels use uppercase `label-md` with `0.04em` tracking to prevent misreading clinical metrics.

## Layout & Spacing

The workstation uses a high-density, multi-pane fluid workspace tailored for high-resolution displays (1080p, 1440p, 4K multi-monitor clinical stations) while retaining operational responsiveness on tablets used at clinical trial sites.

### Layout Model
- **Structural Blueprint:** Sticky consolidated navigation rail (64px collapsed, 240px expanded), coupled with a fluid three-pane layout: Master Cohort List / Form Navigation (280px–340px), Main Case Report Form (CRF) workspace (fluid), and Regulatory Context / Audit Log Drawer (360px collapsible).
- **Tabular & Metric Grids:** Utilizes an 8px sub-grid with strict 4px micro-increments (`space-xs` = 4px, `space-sm` = 8px) for tabular cells to achieve zero wasted vertical space. Table rows default to a compact 32px height with a 40px relaxed review option.

### Breakpoints & Adaptability
- **Desktop High-Res (`>= 1440px`):** Full 3-pane parallel view active simultaneously.
- **Standard Desktop (`1024px – 1439px`):** Main workspace active; audit rail slides out as an overlay or toggles on request.
- **Tablet Bedside Review (`768px – 1023px`):** Single-pane focused form view with bottom-sheet access for adverse reaction logging and site e-signatures.

## Elevation & Depth

This design system rejects heavy, dramatic drop shadows in favor of a clean, clinical depth architecture based on structural borders, subtle surface fills, and crisp micro-contrast.

### Elevation Hierarchy
- **Level 0 (Canvas Base):** `#F8FAFC`. Background canvas upon which all modules sit.
- **Level 1 (Data Cards & Table Panes):** `#FFFFFF` surface bordered by a crisp `1px solid #E2E8F0`. Depth is conveyed through surface contrast against the base canvas, not ambient blur.
- **Level 2 (Sticky Headers & Inline Sub-panels):** `#F1F5F9` with a subtle downward inset rule (`border-b: 1px solid #CBD5E1`) creating visual anchor points during rapid scrolling.
- **Level 3 (Flyouts, Dropdowns, Datepickers):** `#FFFFFF` floating surface bounded by `1px solid #CBD5E1` and an intentional low-spread shadow: `0 4px 12px -2px rgba(15, 23, 42, 0.08)`.
- **Level 4 (Critical Action Modals & Lockout Overlays):** `#FFFFFF` modal bounded by `1px solid #94A3B8` backed by an active clinical scrim: `rgba(15, 23, 42, 0.5)` with `backdrop-filter: blur(2px)`.

### Regulatory Surface Highlighting
Active audit logs and uncommitted e-signatures feature a distinct left-edge structural bar: `3px solid #064E3B` for standard validation, or `3px solid #DC2626` for flagged adverse events.

## Shapes

The interface embraces a low-radius, structured shape language (`roundedness: 1`, base 4px border radius). This produces clean, predictable visual lines that maximize dense data layout without the wasteful bounding boxes caused by hyper-rounded UI elements.

### Radius Assignments
- **Micro UI Elements (Input Fields, Table Badges, Checkboxes):** `4px` (`0.25rem`). Maintains sharp geometric grid alignment.
- **Containers, Cards, & Split Panels:** `6px`–`8px` (`0.375rem`–`0.5rem`). Softens high-density interfaces without breaking architectural structure.
- **Clinical Pills & Status Badges:** Fully rounded (`9999px`) purely for regulatory tag indicators (e.g., `SAE-FLAG`, `ICH-GCP`, `ALCOA+ VERIFIED`) to clearly distinguish interactive pills from square data inputs.

## Components

### Buttons & Action Triggers
- **Primary Clinical Action:** Solid `#064E3B` background, white label, 4px border-radius, compact padding (`8px 14px`), `font-weight: 600`. Active state shifts to `#022c22`.
- **Critical / Freeze Action:** Solid `#DC2626` background, white label. Reserved for trial termination, adverse reaction escalation, and data lock.
- **Secondary Neutral:** `#FFFFFF` background, `1px solid #CBD5E1`, text `#0F172A`. Hover: `#F1F5F9`.
- **Keyboard Shortcuts:** Primary actions expose inline monospace keys (e.g., `⌘S`, `⌥A`) in `code-xs` on the right side of the button label.

### Data Inputs & Clinical Forms
- **Field Anatomy:** Form fields are framed with a `1px solid #CBD5E1` border and `#FFFFFF` background, transitioning to a focused `1px solid #064E3B` border with a crisp `0 0 0 2px rgba(6, 78, 59, 0.15)` focus ring.
- **Audit-Stamped Inputs:** Fields altered post-baseline show a micro amber triangle indicator in the top-right corner, opening the revision history on hover.
- **Monospace Numerical Fields:** Vitals (systolic/diastolic, heart rate, liver function titers) are rendered in `JetBrains Mono` to prevent digit misinterpretation.

### Badges, Status Indicators, & ALCOA+ Tags
- **ALCOA+ Verified:** Emerald-tinted pill (`#ECFDF5` background, `#059669` text, `1px solid #A7F3D0`), displaying an integrated lock icon and monospaced cryptographic signature snippet.
- **Adverse Drug Reaction / Protocol Breach:** Emergency crimson pill (`#FEF2F2` background, `#DC2626` text, `1px solid #FECACA`), animated pulse indicator on active untreated events.
- **Herb-Drug Interaction Warning:** Amber pill (`#FFFBEB` background, `#D97706` text, `1px solid #FDE68A`), flagged alongside active botanicals (e.g., *Curcuma longa* / Warfarin interference flags).

### Data Grid & Tabular Components
- **Column Headers:** Sticky `#F1F5F9` background, `label-md` uppercase text, `1px solid #E2E8F0` borders, equipped with persistent sort, filter, and column-freeze handles.
- **Cell Padding:** Dense vertical padding (`6px 12px`) for high data density; alternating zebra striping (`#FFFFFF` and `#F8FAFC`) to assist horizontal scanning across 20+ variable columns.
- **Row States:** Active selection indicated by a `#ECFDF5` background and a `2px solid #059669` inset border.

### Split-View Review Drawer & Audit Inspector
- Collapsible side panel dedicated to 21 CFR Part 11 electronic records. Displays the complete provenance of the active record: user name, digital signature thumbprint, UTC + IST timestamps, reason for change, and raw hash values.
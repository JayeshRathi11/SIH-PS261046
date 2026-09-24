# COMPLETED_FEATURES.md
# AyuTrial-CTMS – Teammate Handover Documentation
**SIH Problem Statement ID: 26046 | AIIA NPvCC Platform**

---

## Entry #001 — Foundation Setup, ALCOA+ Cryptographic Audit Ledger & 24-Hour SAE State Machine

**Completed:** 2026-09-25
**Engineer:** Lead Systems Architect (Task 1)
**Commit Tag:** `task-1-foundation-alcoa-sae`

---

### 1. Module Name & Feature Overview

| Module | Description |
|--------|-------------|
| `app/core/config.py` | Pydantic Settings (lru_cache singleton), `.env` support |
| `app/core/database.py` | Async SQLAlchemy 2.0 engine, session factory, `get_db` FastAPI dep |
| `app/core/setup_db.py` | One-shot DB setup: table DDL + permission boundary |
| `app/models/clinical.py` | All ORM models + enums |
| `app/services/audit.py` | ALCOA+ SHA-256 hash chaining engine |
| `app/services/safety.py` | SAE business logic + pessimistic locking |
| `app/routers/safety.py` | POST /api/v1/safety/adverse-event |
| `app/routers/audit.py` | GET /api/v1/audit/verify-chain |
| `app/main.py` | FastAPI app factory + lifespan |
| `tests/test_audit_and_sae.py` | Full test harness (13 test cases) |

---

### 2. Database Schemas & Enums

#### `clinical_trials`
```sql
CREATE TABLE clinical_trials (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    protocol_id           VARCHAR(100) NOT NULL UNIQUE,
    ctri_registration_id  VARCHAR(50),
    study_title           VARCHAR(500) NOT NULL,
    status                trial_status_enum NOT NULL DEFAULT 'DRAFT',
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Enum: DRAFT | IEC_APPROVED | CTRI_LINKED | RECRUITING | CLOSED
```

#### `trial_patients`
```sql
CREATE TABLE trial_patients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_id        UUID NOT NULL REFERENCES clinical_trials(id) ON DELETE CASCADE,
    usubjid         VARCHAR(50) NOT NULL,
    prakriti_type   VARCHAR(50),
    baseline_agni   VARCHAR(30),
    consent_status  consent_status_enum NOT NULL DEFAULT 'PENDING',
    enrolled_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (trial_id, usubjid)
);
-- Enum: PENDING | OBTAINED | WITHDRAWN
```

#### `adverse_events`
```sql
CREATE TABLE adverse_events (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id       UUID NOT NULL REFERENCES trial_patients(id) ON DELETE CASCADE,
    clinical_notes   TEXT,
    severity         ae_severity_enum NOT NULL,
    is_serious       BOOLEAN NOT NULL DEFAULT FALSE,
    sae_clock_start  TIMESTAMPTZ,
    sla_deadline     TIMESTAMPTZ,
    status           ae_status_enum NOT NULL DEFAULT 'OPEN',
    reported_by      VARCHAR(100),
    recorded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- AESeverity: MILD | MODERATE | SEVERE | HOSPITALIZATION | LIFE_THREATENING | DEATH
-- AEStatus:   OPEN | UNDER_REVIEW | REPORTED_TO_CDSCO | CLOSED
-- SAE trigger severities: HOSPITALIZATION, LIFE_THREATENING, DEATH
```

#### `alcoa_audit_ledger`
```sql
CREATE TABLE alcoa_audit_ledger (
    sequence_id   BIGSERIAL PRIMARY KEY,
    entity_name   VARCHAR(100) NOT NULL,
    entity_id     VARCHAR(100) NOT NULL,
    action_type   audit_action_enum NOT NULL,
    field_changes JSONB NOT NULL,
    modified_by   VARCHAR(100) NOT NULL,
    timestamp     TIMESTAMPTZ NOT NULL DEFAULT now(),
    prev_hash     VARCHAR(64) NOT NULL,
    current_hash  VARCHAR(64) NOT NULL UNIQUE
);

-- DB-Level permission boundary (applied by setup_db.py):
REVOKE UPDATE   ON TABLE alcoa_audit_ledger FROM ayutrial;
REVOKE DELETE   ON TABLE alcoa_audit_ledger FROM ayutrial;
REVOKE TRUNCATE ON TABLE alcoa_audit_ledger FROM ayutrial;
```

---

### 3. ALCOA+ Hash Chain Formula

```
CurrentHash = SHA256(PrevHash + EntityID + JSONDelta + UserID + Timestamp)
```

- **Genesis block prev_hash**: `GENESIS_BLOCK_HASH_AIIA_CTMS_2026` (constant in config)
- **JSON serialization**: `json.dumps(field_changes, sort_keys=True, default=str)` (deterministic)
- **Hash format**: lowercase hex, 64 characters
- **Implementation**: `app/services/audit.py` — `_compute_hash()` + `append_audit_entry()`

---

### 4. REST API Contracts

#### POST /api/v1/safety/adverse-event

**Request:**
```json
{
  "patient_id": "<UUID>",
  "severity": "HOSPITALIZATION",
  "clinical_notes": "Patient admitted to ICU.",
  "reported_by": "dr_sharma"
}
```

**Response 201:**
```json
{
  "id": "<UUID>",
  "patient_id": "<UUID>",
  "severity": "HOSPITALIZATION",
  "is_serious": true,
  "clinical_notes": "Patient admitted to ICU.",
  "sae_clock_start": "2026-09-25T02:45:00+00:00",
  "sla_deadline":    "2026-09-26T02:45:00+00:00",
  "status": "OPEN",
  "reported_by": "dr_sharma",
  "recorded_at": "2026-09-25T02:45:00+00:00"
}
```

**Business rules:**
- `is_serious = True` iff severity in {HOSPITALIZATION, LIFE_THREATENING, DEATH}
- `sla_deadline = sae_clock_start + 24h` (timezone-aware UTC)
- Pessimistic lock `SELECT ... FOR UPDATE` on patient row
- Returns 404 if patient not found
- Atomic: AE row + audit ledger entry committed together

---

#### GET /api/v1/audit/verify-chain

**Response 200 (clean):**
```json
{
  "status": "VERIFIED_SECURE",
  "total_blocks": 5,
  "tampered_sequence_ids": []
}
```

**Response 200 (tampered):**
```json
{
  "status": "TAMPER_DETECTED",
  "total_blocks": 5,
  "tampered_sequence_ids": [1, 2]
}
```

**Algorithm:**
1. Fetch all rows ORDER BY sequence_id ASC
2. For each row: verify prev_hash linkage AND recompute+compare current_hash
3. Any mismatch → sequence_id added to tampered list
4. Status = TAMPER_DETECTED if list non-empty, else VERIFIED_SECURE

---

### 5. Directory Structure

```
SIH-PS26046/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── setup_db.py
│   ├── models/clinical.py
│   ├── schemas/clinical.py
│   ├── services/
│   │   ├── audit.py
│   │   └── safety.py
│   └── routers/
│       ├── safety.py
│       └── audit.py
├── tests/test_audit_and_sae.py
├── .env / .env.example
├── pytest.ini
├── requirements.txt
└── COMPLETED_FEATURES.md
```

---

### 6. CLI Commands

```powershell
# Start PostgreSQL
docker run -d --name ayutrial-pg -e POSTGRES_USER=ayutrial \
  -e POSTGRES_PASSWORD=ayutrial_secret -e POSTGRES_DB=ayutrial_db \
  -p 5432:5432 postgres:16-alpine

# Setup venv
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Run app
uvicorn app.main:app --reload --port 8000

# Run all tests
.\.venv\Scripts\pytest tests/test_audit_and_sae.py -v

# Specific groups
.\.venv\Scripts\pytest tests/test_audit_and_sae.py::TestAdverseEventCreation -v
.\.venv\Scripts\pytest tests/test_audit_and_sae.py::TestAuditChainVerification -v
.\.venv\Scripts\pytest tests/test_audit_and_sae.py::TestTamperDetection -v
```

---

### 7. Integration Notes

> **NEVER** issue UPDATE/DELETE on `alcoa_audit_ledger` from application code.
> The DB role `ayutrial` has these privileges revoked. Tests use a superuser connection for intentional tamper simulation.

> **Always use timezone-aware datetimes**: `datetime.now(tz=timezone.utc)`.
> Hash computation uses `.isoformat()` which is sensitive to timezone representation.

> **Extending the audit ledger**: Call `await append_audit_entry(db, ...)` BEFORE `await db.commit()`.
> Use `await db.flush()` first to get the entity ID if it is auto-generated.

> **SAE_SEVERITIES constant** in `app/models/clinical.py`: single source of truth for SAE threshold.
> Update only this constant if NDCT Rules change the severity criteria.

> **Test isolation**: Each test TRUNCATEs all tables with RESTART IDENTITY CASCADE.
> This resets BIGSERIAL to 1, which is required for tamper tests asserting sequence_id=1.

---

### 8. Test Coverage (13 Tests)

| Test | Scenario | Expected |
|------|----------|----------|
| `test_mild_ae_does_not_trigger_sae` | MILD severity | is_serious=False, no deadline |
| `test_moderate_ae_does_not_trigger_sae` | MODERATE severity | is_serious=False |
| `test_sae_severities_trigger_24h_clock[HOSPITALIZATION]` | SAE trigger | is_serious=True, +24h deadline |
| `test_sae_severities_trigger_24h_clock[LIFE_THREATENING]` | SAE trigger | is_serious=True, +24h deadline |
| `test_sae_severities_trigger_24h_clock[DEATH]` | SAE trigger | is_serious=True, +24h deadline |
| `test_unknown_patient_returns_404` | Bad patient_id | HTTP 404 |
| `test_empty_ledger_is_verified_secure` | No blocks | VERIFIED_SECURE, 0 blocks |
| `test_single_sae_produces_verified_chain` | 1 block | VERIFIED_SECURE, 1 block |
| `test_multiple_events_chain_is_verified_secure` | 5 blocks | VERIFIED_SECURE, 5 blocks |
| `test_genesis_hash_is_prev_hash_of_first_block` | Genesis link | prev_hash == GENESIS constant |
| `test_tamper_detected_after_raw_sql_mutation` | DBA fraud sim | TAMPER_DETECTED, seq_id=1 |
| `test_tamper_in_middle_of_chain_cascades` | Mid-chain tamper | TAMPER_DETECTED, block 2+ |
| `test_current_hash_mutation_detected` | Hash field tamper | TAMPER_DETECTED |

---

*Task 2+ roadmap: HL7 FHIR R4 serialization, CDISC SDTM export engine, NLP herb-drug matrix, Form CT-16 PDF auto-generation, T-12h/T-4h escalation background workers.*

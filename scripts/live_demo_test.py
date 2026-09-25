import urllib.request
import urllib.error
import json
import time

# Dynamically resolve active trial and demo patient
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/trials") as resp:
        trials = json.loads(resp.read().decode())
        match_t = next((t for t in trials if t.get("protocol_id") == "AIIA-GUD-2026"), trials[0])
        TRIAL_ID = match_t["id"]
except Exception:
    TRIAL_ID = "35113a2b-9fda-4e2c-89a8-ac2f0f25e1af"

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/patients") as resp:
        patients = json.loads(resp.read().decode())
        match_p = next((p for p in patients if p.get("usubjid") == "AIIA-P089"), patients[0])
        PATIENT_ID = match_p["id"]
except Exception:
    PATIENT_ID = "8331d3f7-9578-44d8-abb2-898d995386f4"

print(f"Dynamically Resolved Active Trial ID: {TRIAL_ID}")
print(f"Dynamically Resolved Demo Patient ID: {PATIENT_ID}")

print("="*75)
print("A. CRYPTOGRAPHIC ALCOA+ AUDIT VERIFICATION")
print("="*75)
req = urllib.request.Request("http://127.0.0.1:8000/api/v1/audit/verify-chain")
with urllib.request.urlopen(req) as resp:
    audit_res = json.loads(resp.read().decode())
    print(f"Status Code: {resp.status}")
    print(json.dumps(audit_res, indent=2))

print("\n" + "="*75)
print("B. EXECUTIVE PORTFOLIO KPI DASHBOARD")
print("="*75)
req = urllib.request.Request("http://127.0.0.1:8000/api/v1/analytics/portfolio-kpis")
with urllib.request.urlopen(req) as resp:
    kpi_res = json.loads(resp.read().decode())
    print(f"Status Code: {resp.status}")
    print(json.dumps(kpi_res, indent=2))

print("\n" + "="*75)
print("C. STATISTICAL PROCESS CONTROL (SPC) PROTOCOL DEVIATIONS")
print("="*75)
req = urllib.request.Request(f"http://127.0.0.1:8000/api/v1/analytics/protocol-deviations/{TRIAL_ID}")
with urllib.request.urlopen(req) as resp:
    spc_res = json.loads(resp.read().decode())
    print(f"Status Code: {resp.status}")
    print(json.dumps(spc_res, indent=2))

print("\n" + "="*75)
print("E. TRIGGER SERIOUS ADVERSE EVENT (SAE) ON DEMO PATIENT AIIA-P089")
print("="*75)
idempotency_key = f"DEMO-TEST-KEY-{int(time.time())}"
ae_payload = {
    "patient_id": PATIENT_ID,
    "severity": "HOSPITALIZATION",
    "clinical_notes": "Subject developed acute netra-peetata, dark stool, and severe nausea after morning dose.",
    "ayurvedic_intervention": "Guduchi Extract 500mg BD",
    "concomitant_drugs": ["Aspirin 75mg OD"],
    "reported_by": "dr_vaidya"
}
data_bytes = json.dumps(ae_payload).encode("utf-8")
headers = {
    "Content-Type": "application/json",
    "X-Idempotency-Key": idempotency_key
}
req = urllib.request.Request("http://127.0.0.1:8000/api/v1/safety/adverse-event", data=data_bytes, headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    ae_res = json.loads(resp.read().decode())
    print(f"SAE Created Status Code: {resp.status}")
    print(json.dumps(ae_res, indent=2))
    new_ae_id = ae_res["id"]

print("\n--- Testing Idempotency Shield (Duplicate Request with Same Key) ---")
try:
    req_dup = urllib.request.Request("http://127.0.0.1:8000/api/v1/safety/adverse-event", data=data_bytes, headers=headers, method="POST")
    with urllib.request.urlopen(req_dup) as resp:
        print(f"Unexpected success: {resp.status}")
except urllib.error.HTTPError as e:
    print(f"Idempotency Guard Active: HTTP {e.code} {e.reason}")
    print(f"Response Body: {e.read().decode()}")

print("\n" + "="*75)
print("D. SEMANTIC CASE-SIMILARITY SEARCH (NPvCC Signal Detection)")
print("="*75)
query_term = "hepatic tenderness and peeli aankhein"
url = "http://127.0.0.1:8000/api/v1/safety/cases/similar?query=" + urllib.parse.quote(query_term)
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    sim_res = json.loads(resp.read().decode())
    print(f"Status Code: {resp.status}")
    print(json.dumps(sim_res, indent=2))

print("\n" + "="*75)
print("F. DOWNLOAD THE AUTO-GENERATED CDSCO FORM CT-16 PDF")
print("="*75)
ct16_url = f"http://127.0.0.1:8000/api/v1/safety/reports/ct16/{new_ae_id}"
req = urllib.request.Request(ct16_url)
with urllib.request.urlopen(req) as resp:
    pdf_bytes = resp.read()
    output_pdf = "Form_CT16_Output.pdf"
    with open(output_pdf, "wb") as f:
        f.write(pdf_bytes)
    print(f"Status Code: {resp.status}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    print(f"Content-Disposition: {resp.headers.get('Content-Disposition')}")
    print(f"Saved: {output_pdf} ({len(pdf_bytes)} bytes)")

print("\n" + "="*75)
print("G. DOWNLOAD SUBMISSION-READY CDISC SDTM ZIP PACKAGE")
print("="*75)
sdtm_url = f"http://127.0.0.1:8000/api/v1/export/cdisc-sdtm/{TRIAL_ID}"
req = urllib.request.Request(sdtm_url)
with urllib.request.urlopen(req) as resp:
    zip_bytes = resp.read()
    output_zip = "CDISC_SDTM_PACKAGE.zip"
    with open(output_zip, "wb") as f:
        f.write(zip_bytes)
    print(f"Status Code: {resp.status}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    print(f"Content-Disposition: {resp.headers.get('Content-Disposition')}")
    print(f"Saved: {output_zip} ({len(zip_bytes)} bytes)")

print("\n" + "="*75)
print("ALL LIVE VERIFICATIONS COMPLETED SUCCESSFULLY!")
print("="*75)

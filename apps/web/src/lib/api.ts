export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

export interface RequestOptions extends RequestInit {
  role?: string;
  siteId?: string;
  idempotencyKey?: string;
}

export function getRoleHeaderValue(role?: string): string {
  const map: Record<string, string> = {
    doctor: "DOCTOR",
    coordinator: "CLINICAL_RESEARCH_COORDINATOR",
    npvcc: "NPVCC_OFFICER",
    auditor: "REGULATORY_AUDITOR",
  };
  return map[role || "doctor"] || "DOCTOR";
}

export async function apiFetch<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { role, siteId, idempotencyKey, headers = {}, ...rest } = options;

  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const defaultHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    "X-User-Role": getRoleHeaderValue(role),
    "X-Site-Id": siteId || "SITE-01",
  };

  if (rest.method && rest.method !== "GET" && rest.method !== "HEAD") {
    defaultHeaders["X-Idempotency-Key"] =
      idempotencyKey || `IDEMP-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
  }

  const response = await fetch(url, {
    ...rest,
    headers: {
      ...defaultHeaders,
      ...(headers as Record<string, string>),
    },
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorDetail;
    } catch {
      // not json
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export async function downloadBlob(endpoint: string, filename: string): Promise<void> {
  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "X-User-Role": "REGULATORY_AUDITOR",
      "X-Site-Id": "SITE-01",
    },
  });

  if (!response.ok) {
    throw new Error(`Download failed with status ${response.status}`);
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(downloadUrl);
}

// Typed API operations
export const api = {
  // Audit
  verifyChain: () => apiFetch("/audit/verify-chain"),
  getMerkleRoot: () => apiFetch("/audit/merkle-root"),

  // Analytics
  getPortfolioKPIs: () => apiFetch("/analytics/portfolio-kpis"),

  // Concurrency Locking
  acquireLock: (recordId: string, fieldName: string, userId: string) =>
    apiFetch("/locks/acquire", {
      method: "POST",
      body: JSON.stringify({
        record_id: recordId,
        field_name: fieldName,
        user_id: userId,
        ttl_seconds: 30,
      }),
    }),
  releaseLock: (recordId: string, fieldName: string, userId: string) =>
    apiFetch("/locks/release", {
      method: "POST",
      body: JSON.stringify({
        record_id: recordId,
        field_name: fieldName,
        user_id: userId,
      }),
    }),

  // eCRF & Patients
  saveECRF: (patientId: string, payload: any, role?: string, siteId?: string) =>
    apiFetch(`/patients/${patientId}/ecrf`, {
      method: "POST",
      role,
      siteId,
      body: JSON.stringify(payload),
    }),

  // Safety & Adverse Events
  submitAdverseEvent: (payload: any, role?: string, siteId?: string) =>
    apiFetch("/safety/adverse-event", {
      method: "POST",
      role,
      siteId,
      body: JSON.stringify(payload),
    }),

  // Protocol State Transitions
  advanceTrialStatus: (trialId: string, payload: any, role?: string) =>
    apiFetch(`/trials/${trialId}/advance-status`, {
      method: "PUT",
      role,
      body: JSON.stringify(payload),
    }),

  // File Downloads
  downloadFormCT16: (aeId: string) =>
    downloadBlob(`/safety/reports/ct16/${aeId}`, `CDSCO_Form_CT16_${aeId}.pdf`),
  downloadCDISCSdtm: (trialId: string) =>
    downloadBlob(`/export/cdisc-sdtm/${trialId}`, `CDISC_SDTM_${trialId}.zip`),
  downloadFHIRBundle: (patientId: string) =>
    downloadBlob(`/export/fhir-bundle/${patientId}`, `FHIR_Bundle_${patientId}.json`),
};

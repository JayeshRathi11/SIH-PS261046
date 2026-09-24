export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

export interface RequestOptions extends RequestInit {
  role?: string;
  siteId?: string;
  userId?: string;
  idempotencyKey?: string;
}

export function getRoleHeaderValue(role?: string): string {
  const map: Record<string, string> = {
    doctor: "DOCTOR",
    coordinator: "CLINICAL_RESEARCH_COORDINATOR",
    npvcc: "NPVCC_OFFICER",
    auditor: "REGULATORY_AUDITOR",
    admin: "SUPER_ADMIN",
    super_admin: "SUPER_ADMIN",
  };
  return map[role?.toLowerCase() || ""] || (role ? role.toUpperCase() : "DOCTOR");
}

export function getActiveSessionHeaders(): Record<string, string> {
  if (typeof window !== "undefined") {
    try {
      const raw = localStorage.getItem("ayutrial_session");
      if (raw) {
        const session = JSON.parse(raw);
        return {
          "X-User-Role": session.roleHeader || getRoleHeaderValue(session.role) || "DOCTOR",
          "X-Site-Id": session.siteId || "SITE-01",
          "X-User-Id": session.id || "USER-PI-01",
          ...(session.token ? { Authorization: `Bearer ${session.token}` } : {}),
        };
      }
    } catch {
      // Fallback below
    }
  }
  return {
    "X-User-Role": "DOCTOR",
    "X-Site-Id": "SITE-01",
    "X-User-Id": "USER-PI-01",
  };
}

export async function apiFetch<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { role, siteId, userId, idempotencyKey, headers = {}, ...rest } = options;
  const sessionHeaders = getActiveSessionHeaders();

  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const defaultHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    "X-User-Role": role ? getRoleHeaderValue(role) : sessionHeaders["X-User-Role"],
    "X-Site-Id": siteId || sessionHeaders["X-Site-Id"],
    "X-User-Id": userId || sessionHeaders["X-User-Id"],
    ...(sessionHeaders["Authorization"] ? { Authorization: sessionHeaders["Authorization"] } : {}),
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

  const sessionHeaders = getActiveSessionHeaders();

  const response = await fetch(url, {
    method: "GET",
    headers: {
      "X-User-Role": "REGULATORY_AUDITOR",
      "X-Site-Id": sessionHeaders["X-Site-Id"] || "SITE-01",
      "X-User-Id": sessionHeaders["X-User-Id"] || "USER-AUD-01",
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

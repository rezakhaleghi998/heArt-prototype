export const API_BASE = "/api/proxy";

export type ApplicationStatus = "draft" | "submitted" | "screening" | "reviewed";
export type AssetKind = "profile_image" | "intro_video" | "portfolio";

export type CandidatePayload = {
  full_name: string;
  email: string;
  phone?: string;
  city?: string;
};

export type ApplicationPayload = {
  candidate: CandidatePayload;
  role: string;
  short_bio?: string;
  years_experience?: number;
  skills: string[];
  availability?: string;
  portfolio_links: string[];
  gdpr_consent: boolean;
};

export type Application = {
  id: string;
  candidate: CandidatePayload & { id: string };
  role: string;
  short_bio?: string;
  years_experience?: number;
  skills: string[];
  availability?: string;
  portfolio_links: string[];
  status: ApplicationStatus;
  completion_percent: number;
  submitted_at?: string;
  media_assets: Array<{
    id: string;
    kind: AssetKind;
    file_name: string;
    content_type: string;
    size_bytes: number;
    storage_key: string;
    public_url?: string;
    uploaded: boolean;
  }>;
  screening_result?: {
    status: "pending" | "completed" | "failed";
    summary?: string;
    strengths: string[];
    risks: string[];
    fit_score?: number;
    recommended_next_action?: string;
  };
  created_at: string;
  updated_at: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
      cache: "no-store"
    });
  } catch {
    throw new Error("Backend non raggiungibile. Verifica BACKEND_URL sul frontend e lo stato del backend Railway.");
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Errore API" }));
    throw new Error(error.detail ?? "Errore API");
  }
  return response.json() as Promise<T>;
}

export const api = {
  createApplication: (payload: ApplicationPayload) =>
    request<Application>("/applications", { method: "POST", body: JSON.stringify(payload) }),
  getApplication: (id: string) =>
    request<Application>(`/applications/${id}`),
  updateApplication: (id: string, payload: ApplicationPayload) =>
    request<Application>(`/applications/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  submitApplication: (id: string) =>
    request<Application>(`/applications/${id}/submit`, { method: "POST" }),
  listApplications: (status?: string) =>
    request<{ items: Application[]; total: number }>(`/applications${status ? `?status=${status}` : ""}`),
  initUpload: (payload: { application_id: string; kind: AssetKind; file_name: string; content_type: string; size_bytes: number }) =>
    request<{ asset_id: string; upload_url: string; storage_key: string; headers: Record<string, string> }>("/uploads/init", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  uploadDirect: async (asset_id: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    let response: Response;
    try {
      response = await fetch(`${API_BASE}/uploads/${asset_id}/file`, {
        method: "POST",
        body: formData,
        cache: "no-store"
      });
    } catch {
      throw new Error("Backend upload non raggiungibile. Verifica BACKEND_URL sul frontend e lo stato del backend Railway.");
    }
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Errore upload" }));
      throw new Error(error.detail ?? "Errore upload");
    }
    return response.json();
  },
  confirmUpload: (asset_id: string, public_url?: string) =>
    request("/uploads/confirm", { method: "POST", body: JSON.stringify({ asset_id, public_url }) })
};

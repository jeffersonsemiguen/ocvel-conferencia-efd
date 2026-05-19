import { clearAuth, getToken } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData;
  const token = getToken();

  const headers: Record<string, string> = {};
  if (!isFormData) headers["Content-Type"] = "application/json";
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (init?.headers) Object.assign(headers, init.headers);

  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });

  if (res.status === 401) {
    clearAuth();
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Sessão expirada");
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(
      Array.isArray(error.detail)
        ? error.detail.map((e: { msg?: string }) => e.msg ?? e).join("; ")
        : error.detail ?? "Erro na requisição"
    );
  }
  return res.json();
}

async function downloadFile(path: string, filename?: string): Promise<void> {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { headers });

  if (res.status === 401) {
    clearAuth();
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Sessão expirada");
  }
  if (!res.ok) throw new Error("Erro ao baixar arquivo");

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename ?? path.split("/").pop() ?? "download";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export const api = {
  get:      <T>(path: string)                    => request<T>(path),
  post:     <T>(path: string, body: unknown)     => request<T>(path, { method: "POST",  body: JSON.stringify(body) }),
  patch:    <T>(path: string, body: unknown)     => request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete:   <T>(path: string)                    => request<T>(path, { method: "DELETE" }),
  upload:   <T>(path: string, form: FormData)    => request<T>(path, { method: "POST",  body: form }),
  download: (path: string, filename?: string)    => downloadFile(path, filename),
};

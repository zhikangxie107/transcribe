const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const STORAGE_KEY = "authTokens";

let auth = loadAuth();

function loadAuth() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
  catch { return {}; }
}
function saveAuth(next) {
  auth = { ...auth, ...next };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
}
function clearAuth() {
  auth = {};
  localStorage.removeItem(STORAGE_KEY);
}

function decodeJwtExpMs(token) {
  try {
    const b64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = JSON.parse(decodeURIComponent(escape(atob(b64))));
    return (json.exp || 0) * 1000;
  } catch { return 0; }
}

function isExpiredSoon() {
  if (!auth.idToken) return true;
  const now = Date.now();
  const exp = auth.expMs || decodeJwtExpMs(auth.idToken);
  return now > exp - 60_000; // refresh 60s early
}

async function refreshToken() {
  if (!auth.refreshToken) throw new Error("Missing refresh token");
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: auth.refreshToken }),
  });
  if (!res.ok) {
    clearAuth();
    throw new Error("Token refresh failed");
  }
  const data = await res.json();
  saveAuth({
    idToken: data.id_token,
    refreshToken: data.refresh_token || auth.refreshToken,
    uid: data.uid,
    expMs: decodeJwtExpMs(data.id_token),
  });
}

async function ensureFreshAuth() {
  if (!auth.idToken) throw new Error("Not authenticated");
  if (isExpiredSoon()) await refreshToken();
}

async function fetchWithAuth(path, { method = "GET", headers = {}, body, authRequired = true } = {}) {
  if (authRequired) {
    await ensureFreshAuth();
    headers = { ...headers, Authorization: `Bearer ${auth.idToken}` };
  }
  let res = await fetch(`${API_BASE}${path}`, { method, headers, body });
  if (res.status === 401 && authRequired && auth.refreshToken) {
    // one retry after refresh
    await refreshToken();
    headers = { ...headers, Authorization: `Bearer ${auth.idToken}` };
    res = await fetch(`${API_BASE}${path}`, { method, headers, body });
  }
  return res;
}

// Auth
export async function signup({ email, password, displayName }) {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, display_name: displayName }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail?.message || "Signup failed");
  saveAuth({
    idToken: data.id_token,
    refreshToken: data.refresh_token,
    uid: data.uid,
    expMs: decodeJwtExpMs(data.id_token),
  });
  return data;
}

export async function login({ email, password }) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail?.message || "Login failed");
  saveAuth({
    idToken: data.id_token,
    refreshToken: data.refresh_token,
    uid: data.uid,
    expMs: decodeJwtExpMs(data.id_token),
  });
  return data;
}

export function logout() { clearAuth(); }

export function isLoggedIn() { return !!auth.idToken; }

export function getIdToken() { return auth.idToken || null; }

export async function me() {
  const res = await fetchWithAuth("/auth/me");
  if (!res.ok) throw new Error("Failed to fetch profile");
  return res.json(); // { uid, email, display_name, photo_url, email_verified }
}

export async function transcribeAudio(file, { language } = {}) {
  const fd = new FormData();
  fd.append("audio", file);
  if (language) fd.append("language", language);

  const res = await fetchWithAuth("/transcripts/transcribe", {
    method: "POST",
    body: fd,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Transcription failed");
  return data;
}

export async function listTranscripts() {
  const res = await fetchWithAuth("/transcripts");
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Failed to list transcripts");
  return data;
}

export async function getTranscript(id) {
  const res = await fetchWithAuth(`/transcripts/${id}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Transcript not found");
  return data;
}

export async function createTranscript({ text, words = [], filename } = {}) {
  const res = await fetchWithAuth("/transcripts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, words, filename }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Failed to create transcript");
  return data;
}

export async function updateTranscript(id, { text, filename } = {}) {
  const res = await fetchWithAuth(`/transcripts/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, filename }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || "Failed to update transcript");
  return data;
}

export async function deleteTranscript(id) {
  const res = await fetchWithAuth(`/transcripts/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data?.detail || "Failed to delete transcript");
  }
  return { ok: true };
}


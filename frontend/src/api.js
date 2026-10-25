const BASE = import.meta.env.VITE_API_URL || "";
const KEY = "foodverse.settings";

export function loadSettings() {
  try { return JSON.parse(sessionStorage.getItem(KEY)) || { provider: "gemini", apiKey: "" }; }
  catch { return { provider: "gemini", apiKey: "" }; }
}
export function saveSettings(s) {
  try { sessionStorage.setItem(KEY, JSON.stringify(s)); } catch { /* private mode */ }
}

async function request(path, options = {}) {
  const s = loadSettings();
  const headers = { ...(options.headers || {}), "X-Provider": s.provider };
  if (s.apiKey) headers["X-API-Key"] = s.apiKey;
  let res;
  try { res = await fetch(BASE + path, { ...options, headers }); }
  catch { throw new Error("Cannot reach the FoodVerse server. Check that the backend is running on port 8000."); }
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const j = await res.json();
      msg = typeof j.detail === "string" ? j.detail : Array.isArray(j.detail) ? j.detail.map((d) => d.msg).join("; ") : msg;
    } catch { /* non-JSON error */ }
    throw new Error(msg);
  }
  return res.json();
}

const upload = (path, file, extra = {}) => {
  const fd = new FormData();
  fd.append("file", file);
  Object.entries(extra).forEach(([k, v]) => fd.append(k, v));
  return request(path, { method: "POST", body: fd });
};
const json = (path, body) =>
  request(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

export const api = {
  health: () => request("/api/health"),
  nutrition: (f) => upload("/api/nutrition", f),
  freshness: (f, item) => upload("/api/freshness", f, { item }),
  hygiene: (f) => upload("/api/hygiene", f),
  recipes: (b) => json("/api/recipes", b),
  mealplan: (b) => json("/api/mealplan", b),
  history: () => request("/api/history"),
  clearHistory: () => request("/api/history", { method: "DELETE" }),
};

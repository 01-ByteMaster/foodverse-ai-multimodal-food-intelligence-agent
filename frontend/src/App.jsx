import { useEffect, useState } from "react";
import { api, loadSettings, saveSettings } from "./api";
import { Btn, Card } from "./components/ui";
import Home from "./pages/Home";
import Recognition from "./pages/Recognition";
import Freshness from "./pages/Freshness";
import Hygiene from "./pages/Hygiene";
import Recipes from "./pages/Recipes";
import Planner from "./pages/Planner";

const TABS = [
  ["home", "Home", Home], ["recognition", "Nutrition", Recognition], ["freshness", "Freshness", Freshness],
  ["hygiene", "Hygiene", Hygiene], ["recipes", "Recipes", Recipes], ["planner", "Planner", Planner],
];

export default function App() {
  const [tab, setTab] = useState(() => window.location.hash.slice(1) || "home");
  const [open, setOpen] = useState(false);
  const [settings, setSettings] = useState(loadSettings);
  const [mode, setMode] = useState("demo");
  const [server, setServer] = useState("checking");

  const go = (t) => { setTab(t); window.location.hash = t; window.scrollTo(0, 0); };
  useEffect(() => {
    const h = () => setTab(window.location.hash.slice(1) || "home");
    window.addEventListener("hashchange", h);
    return () => window.removeEventListener("hashchange", h);
  }, []);
  useEffect(() => {
    api.health().then((r) => { setMode(r.mode); setServer("online"); }).catch(() => setServer("offline"));
  }, [settings]);

  const save = (s) => { setSettings(s); saveSettings(s); setOpen(false); };
  const Page = (TABS.find((t) => t[0] === tab) || TABS[0])[2];

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <nav className="nav">
        <button className="logo" onClick={() => go("home")} aria-label="FoodVerse AI home"><span>FoodVerse</span><b>AI</b></button>
        <div className="tabs-nav" role="tablist">
          {TABS.filter((t) => t[0] !== "home").map(([id, label]) => (
            <button key={id} role="tab" aria-selected={tab === id} className={tab === id ? "on" : ""} onClick={() => go(id)}>{label}</button>
          ))}
        </div>
        <button className={`status ${server === "offline" ? "bad" : mode === "live" ? "live" : ""}`} onClick={() => setOpen(true)}>
          {server === "offline" ? "Server offline" : mode === "live" ? "Live AI" : "Demo mode"} - Settings
        </button>
      </nav>
      <main id="main" className="wrap-main"><Page go={go} /></main>
      <footer className="foot">FoodVerse AI is an assistant, not a medical or legal food-safety authority. When in doubt, throw it out.</footer>
      {open && <Settings value={settings} onSave={save} onClose={() => setOpen(false)} />}
    </>
  );
}

function Settings({ value, onSave, onClose }) {
  const [s, setS] = useState(value);
  useEffect(() => {
    const k = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, [onClose]);
  return (
    <div className="overlay" onClick={onClose}>
      <Card color="white" className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-label="Settings">
        <h2>AI settings</h2>
        <label className="field">Provider
          <select value={s.provider} onChange={(e) => setS({ ...s, provider: e.target.value })}>
            <option value="gemini">Google Gemini</option><option value="groq">Groq (Llama)</option>
          </select></label>
        <label className="field">API key
          <input type="password" autoComplete="off" value={s.apiKey} onChange={(e) => setS({ ...s, apiKey: e.target.value })} placeholder="Paste your key, or leave empty for demo mode" /></label>
        <p className="muted">Your key stays in this browser tab (session storage) and is sent only to your own FoodVerse server with each request. It is never saved on the server.</p>
        <div className="row gap">
          <Btn color="mint" onClick={() => onSave(s)}>Save settings</Btn>
          <Btn color="white" onClick={() => onSave({ ...s, apiKey: "" })}>Switch to demo mode</Btn>
          <Btn color="white" onClick={onClose}>Cancel</Btn>
        </div>
      </Card>
    </div>
  );
}

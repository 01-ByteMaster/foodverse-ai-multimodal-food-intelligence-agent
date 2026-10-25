import { useEffect, useRef, useState } from "react";

export const Card = ({ color = "white", className = "", children, ...p }) => (
  <section className={`card bg-${color} ${className}`} {...p}>{children}</section>
);

export const Btn = ({ color = "lemon", className = "", ...p }) => (
  <button className={`btn bg-${color} ${className}`} {...p} />
);

export const Badge = ({ color = "white", children }) => <span className={`badge bg-${color}`}>{children}</span>;

export function Loading({ text = "Analysing" }) {
  return (
    <div className="loading" role="status">
      <span className="blocks"><i /><i /><i /></span>
      <b>{text}...</b>
    </div>
  );
}

export const ErrorBox = ({ message, onClose }) =>
  message ? (
    <div className="errorbox" role="alert">
      <div><b>Something went wrong.</b> {message}</div>
      {onClose && <button className="btn bg-white small" onClick={onClose}>Dismiss</button>}
    </div>
  ) : null;

export function DemoNote({ mode }) {
  if (mode !== "demo") return null;
  return (
    <div className="demonote">
      Demo mode: this is sample or heuristic output. Add a Gemini or Groq key in Settings for real AI analysis.
    </div>
  );
}

export function Uploader({ accept = "image/*", file, onFile, hint = "Drop an image here or click to browse", video = false }) {
  const input = useRef();
  const [drag, setDrag] = useState(false);
  const [url, setUrl] = useState(null);

  useEffect(() => {
    if (!file) { setUrl(null); return; }
    const u = URL.createObjectURL(file);
    setUrl(u);
    return () => URL.revokeObjectURL(u);
  }, [file]);

  const pick = (f) => f && onFile(f);
  const isVideo = file && file.type.startsWith("video");

  return (
    <div
      className={`uploader ${drag ? "drag" : ""} ${file ? "has" : ""}`}
      onClick={() => input.current.click()}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files[0]); }}
      role="button" tabIndex={0}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && input.current.click()}
      aria-label={hint}
    >
      <input ref={input} type="file" accept={accept} hidden onChange={(e) => pick(e.target.files[0])} />
      {url ? (
        isVideo ? <video src={url} controls onClick={(e) => e.stopPropagation()} /> : <img src={url} alt="Selected upload" />
      ) : (
        <div className="empty">
          <div className="plus">+</div>
          <p>{hint}</p>
          <small>{video ? "JPG, PNG, WEBP up to 8 MB, or MP4/MOV video up to 40 MB" : "JPG, PNG or WEBP up to 8 MB"}</small>
        </div>
      )}
    </div>
  );
}

export function Bar({ label, value, max, unit = "g", color = "mint" }) {
  const pct = Math.max(2, Math.min(100, (value / (max || 1)) * 100));
  return (
    <div className="bar">
      <div className="bar-head"><span>{label}</span><b>{Math.round(value)}{unit}</b></div>
      <div className="bar-track"><div className={`bar-fill bg-${color}`} style={{ width: `${pct}%` }} /></div>
    </div>
  );
}

export function Ring({ value, label, color }) {
  const c = color || (value >= 75 ? "var(--mint)" : value >= 50 ? "var(--lemon)" : "var(--tomato)");
  return (
    <div className="ring" style={{ background: `conic-gradient(${c} ${value * 3.6}deg, #fff 0)` }} role="img" aria-label={`${label} ${value}`}>
      <div className="ring-in"><b>{value}</b><small>{label}</small></div>
    </div>
  );
}

export function MacroDonut({ protein, carbs, fat }) {
  const p = protein * 4, c = carbs * 4, f = fat * 9, t = p + c + f || 1;
  const a = (p / t) * 360, b = a + (c / t) * 360;
  return (
    <div className="donut-wrap">
      <div className="donut" style={{ background: `conic-gradient(var(--sky) 0 ${a}deg, var(--lemon) ${a}deg ${b}deg, var(--tomato) ${b}deg 360deg)` }} />
      <ul className="legend">
        <li><i className="bg-sky" />Protein {Math.round((p / t) * 100)}%</li>
        <li><i className="bg-lemon" />Carbs {Math.round((c / t) * 100)}%</li>
        <li><i className="bg-tomato" />Fat {Math.round((f / t) * 100)}%</li>
      </ul>
    </div>
  );
}

export const PageHead = ({ title, sub, color }) => (
  <header className={`pagehead bg-${color}`}>
    <h1>{title}</h1>
    <p>{sub}</p>
  </header>
);

export const List = ({ items, empty = "Nothing to show." }) =>
  items?.length ? <ul className="plain">{items.map((t, i) => <li key={i}>{t}</li>)}</ul> : <p className="muted">{empty}</p>;

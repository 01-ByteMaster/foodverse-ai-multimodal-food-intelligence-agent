import { useState } from "react";
import { api } from "../api";
import { Badge, Btn, Card, DemoNote, ErrorBox, List, Loading, PageHead } from "../components/ui";

export default function Recipes() {
  const [tags, setTags] = useState([]);
  const [text, setText] = useState("");
  const [diet, setDiet] = useState("any");
  const [mins, setMins] = useState(30);
  const [serv, setServ] = useState(2);
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const add = () => {
    const items = text.split(",").map((s) => s.trim()).filter(Boolean);
    if (items.length) setTags([...new Set([...tags, ...items])].slice(0, 30));
    setText("");
  };
  const run = async () => {
    setBusy(true); setErr(""); setRes(null);
    try { setRes(await api.recipes({ ingredients: tags, diet, max_minutes: Number(mins), servings: Number(serv) })); }
    catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  return (
    <>
      <PageHead color="tomato" title="Smart kitchen assistant" sub="Tell us what is in your pantry. Get recipes with timings, steps and swaps for what you are missing." />
      <div className="grid two">
        <Card>
          <label className="field">Pantry ingredients
            <div className="row gap">
              <input value={text} onChange={(e) => setText(e.target.value)} placeholder="eggs, spinach, rice"
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), add())} />
              <Btn color="white" onClick={add} type="button">Add</Btn>
            </div>
          </label>
          <div className="row wrap gap tags">
            {tags.length === 0 && <span className="muted">No ingredients yet. Separate several with commas.</span>}
            {tags.map((t) => <button key={t} className="tag" onClick={() => setTags(tags.filter((x) => x !== t))} aria-label={`Remove ${t}`}>{t} x</button>)}
          </div>
          <div className="grid three tight">
            <label className="field">Diet
              <select value={diet} onChange={(e) => setDiet(e.target.value)}>
                {["any", "vegetarian", "vegan", "keto", "diabetic-friendly", "high-protein"].map((d) => <option key={d}>{d}</option>)}
              </select></label>
            <label className="field">Max minutes
              <input type="number" min="5" max="240" value={mins} onChange={(e) => setMins(e.target.value)} /></label>
            <label className="field">Servings
              <input type="number" min="1" max="12" value={serv} onChange={(e) => setServ(e.target.value)} /></label>
          </div>
          <Btn color="tomato" className="full" disabled={!tags.length || busy} onClick={run}>{busy ? "Cooking up ideas..." : "Get recipes"}</Btn>
        </Card>
        <div className="stack">
          <ErrorBox message={err} onClose={() => setErr("")} />
          {busy && <Card><Loading text="Writing recipes" /></Card>}
          {!res && !busy && !err && <Card className="placeholder"><h3>Recipes appear here</h3><p>Add at least one ingredient to start.</p></Card>}
          {res && <DemoNote mode={res.mode} />}
          {res?.recipes.map((r, i) => (
            <Card key={i}>
              <h2>{r.name}</h2>
              <div className="row wrap gap">
                <Badge color="lemon">{r.cook_time_min} min</Badge><Badge color="sky">{r.difficulty}</Badge>
                <Badge>{r.servings} servings</Badge>
                {r.calories_per_serving ? <Badge color="mint">{r.calories_per_serving} kcal each</Badge> : null}
                {r.protein_g ? <Badge color="grape">{r.protein_g} g protein</Badge> : null}
              </div>
              <h3>Ingredients</h3>
              <ul className="plain">{r.ingredients.map((g, k) => (
                <li key={k}>{g.have ? "Have" : "Need"}: <b>{g.item}</b> <span className="muted">{g.amount}</span></li>))}</ul>
              <h3>Steps</h3>
              <ol className="steps">{r.steps.map((s, k) => <li key={k}>{s}</li>)}</ol>
              {r.substitutions?.length > 0 && (<><h3>Swaps</h3>
                <List items={r.substitutions.map((s) => `${s.missing}: try ${s.alternative}`)} /></>)}
              {r.tip && <p className="tipbox"><b>Chef tip.</b> {r.tip}</p>}
            </Card>
          ))}
        </div>
      </div>
    </>
  );
}

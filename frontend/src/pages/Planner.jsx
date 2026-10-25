import { useState } from "react";
import { api } from "../api";
import { Badge, Bar, Btn, Card, DemoNote, ErrorBox, Loading, PageHead } from "../components/ui";

const init = { age: 28, gender: "male", weight_kg: 70, height_cm: 172, activity: "moderate", goal: "maintain", diet: "standard", allergies: "" };

export default function Planner() {
  const [p, setP] = useState(init);
  const [res, setRes] = useState(null);
  const [day, setDay] = useState(0);
  const [checked, setChecked] = useState({});
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const set = (k) => (e) => setP({ ...p, [k]: e.target.value });

  const run = async (e) => {
    e.preventDefault();
    setBusy(true); setErr(""); setRes(null); setChecked({});
    try {
      setRes(await api.mealplan({ ...p, age: +p.age, weight_kg: +p.weight_kg, height_cm: +p.height_cm }));
      setDay(0);
    } catch (e2) { setErr(e2.message); } finally { setBusy(false); }
  };
  const t = res?.targets;
  const d = res?.days?.[day];

  return (
    <>
      <PageHead color="grape" title="Personalised meal planner" sub="Your numbers in, a 7-day plan and a shopping list out. Calories come from the Mifflin-St Jeor formula." />
      <div className="grid two">
        <Card>
          <form onSubmit={run}>
            <div className="grid two tight">
              <label className="field">Age<input type="number" min="14" max="100" value={p.age} onChange={set("age")} required /></label>
              <label className="field">Gender<select value={p.gender} onChange={set("gender")}><option value="male">Male</option><option value="female">Female</option></select></label>
              <label className="field">Weight (kg)<input type="number" min="30" max="300" step="0.1" value={p.weight_kg} onChange={set("weight_kg")} required /></label>
              <label className="field">Height (cm)<input type="number" min="120" max="230" value={p.height_cm} onChange={set("height_cm")} required /></label>
            </div>
            <label className="field">Activity level
              <select value={p.activity} onChange={set("activity")}>
                <option value="sedentary">Sedentary (desk job, little exercise)</option><option value="light">Light (1-3 workouts a week)</option>
                <option value="moderate">Moderate (3-5 workouts a week)</option><option value="active">Active (6-7 workouts a week)</option>
                <option value="athlete">Athlete (twice-daily training)</option></select></label>
            <div className="grid two tight">
              <label className="field">Goal<select value={p.goal} onChange={set("goal")}><option value="fat_loss">Fat loss</option><option value="maintain">Maintain</option><option value="muscle_gain">Muscle gain</option></select></label>
              <label className="field">Diet<select value={p.diet} onChange={set("diet")}><option value="standard">Standard</option><option value="vegetarian">Vegetarian</option><option value="vegan">Vegan</option><option value="keto">Keto</option><option value="diabetic">Diabetic-friendly</option></select></label>
            </div>
            <label className="field">Allergies or dislikes (optional)<input value={p.allergies} onChange={set("allergies")} placeholder="peanuts, mushrooms" maxLength={120} /></label>
            <Btn color="grape" className="full" disabled={busy} type="submit">{busy ? "Planning..." : "Build my 7-day plan"}</Btn>
          </form>
        </Card>
        <div className="stack">
          <ErrorBox message={err} onClose={() => setErr("")} />
          {busy && <Card><Loading text="Calculating targets and planning meals" /></Card>}
          {!res && !busy && !err && <Card className="placeholder"><h3>Your plan appears here</h3><p>Fill in your profile and press Build.</p></Card>}
          {res && (
            <>
              <DemoNote mode={res.mode} />
              {res.mode === "demo" && p.allergies && <div className="demonote">Allergies are only applied with a live AI key. Check the demo meals yourself.</div>}
              <Card color="lemon">
                <h2>{t.calories} kcal a day</h2>
                <div className="row wrap gap"><Badge>BMR {t.bmr}</Badge><Badge>TDEE {t.tdee}</Badge><Badge>BMI {t.bmi}</Badge></div>
                <div className="grid three tight top">
                  <Bar label="Protein" value={t.protein_g} max={Math.max(t.protein_g, t.carbs_g, t.fat_g)} color="sky" />
                  <Bar label="Carbs" value={t.carbs_g} max={Math.max(t.protein_g, t.carbs_g, t.fat_g)} color="white" />
                  <Bar label="Fat" value={t.fat_g} max={Math.max(t.protein_g, t.carbs_g, t.fat_g)} color="tomato" />
                </div>
              </Card>
              <Card>
                <div className="tabs" role="tablist">
                  {res.days.map((x, i) => <button key={i} role="tab" aria-selected={i === day} className={i === day ? "on" : ""} onClick={() => setDay(i)}>{x.day.slice(0, 3)}</button>)}
                </div>
                {d && (<>
                  <h3>{d.day} <span className="muted">{d.total_calories} kcal</span></h3>
                  <ul className="plain">{d.meals.map((m, i) => (
                    <li key={i} className="meal">
                      <div className="row between wrap"><b>{m.type}: {m.name}</b><Badge color="lemon">{m.calories} kcal</Badge></div>
                      <span className="muted">P {m.protein_g} g, C {m.carbs_g} g, F {m.fat_g} g. {m.portion}</span>
                      <div className="row wrap gap">{m.items?.map((x) => <Badge key={x}>{x}</Badge>)}</div>
                    </li>))}</ul>
                </>)}
              </Card>
              <Card color="mint" className="grocery">
                <div className="row between wrap"><h3>Grocery list</h3><Btn color="white" className="small" onClick={() => window.print()}>Print</Btn></div>
                <div className="grid two tight">
                  {Object.entries(res.grocery).filter(([, v]) => v?.length).map(([cat, items]) => (
                    <div key={cat}><h4>{cat}</h4>
                      {items.map((it) => (
                        <label key={it} className="check"><input type="checkbox" checked={!!checked[it]} onChange={(e) => setChecked({ ...checked, [it]: e.target.checked })} /><span>{it}</span></label>))}
                    </div>))}
                </div>
              </Card>
            </>
          )}
        </div>
      </div>
    </>
  );
}

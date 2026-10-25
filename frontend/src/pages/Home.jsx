import { useEffect, useState } from "react";
import { api } from "../api";
import { Badge, Btn, Card } from "../components/ui";

const MODULES = [
  { id: "recognition", color: "lemon", title: "Food recognition", text: "Photo in, dish, calories and macros out." },
  { id: "freshness", color: "mint", title: "Freshness check", text: "Fresh, moderately fresh or spoiled, with storage advice." },
  { id: "hygiene", color: "sky", title: "Kitchen hygiene", text: "Gloves, hairnets and cross-contamination, scored." },
  { id: "recipes", color: "tomato", title: "Recipe assistant", text: "Cook with what you already have." },
  { id: "planner", color: "grape", title: "Meal planner", text: "A 7-day plan and shopping list for your goal." },
];

const KIND = { nutrition: "Nutrition", freshness: "Freshness", hygiene: "Hygiene", recipes: "Recipes", mealplan: "Meal plan" };

export default function Home({ go }) {
  const [hist, setHist] = useState([]);
  useEffect(() => { api.history().then(setHist).catch(() => {}); }, []);
  const clear = () => api.clearHistory().then(() => setHist([])).catch(() => {});

  return (
    <>
      <section className="hero">
        <h1 className="stamp s1">Point a camera at your food.</h1>
        <h1 className="stamp s2">Get the whole story.</h1>
        <p>FoodVerse AI reads photos and kitchen videos to tell you what is on the plate, whether it is safe, and what to eat next.</p>
        <Btn color="lemon" onClick={() => go("recognition")}>Analyse a meal</Btn>
      </section>
      <div className="grid modules">
        {MODULES.map((m) => (
          <button key={m.id} className={`module bg-${m.color}`} onClick={() => go(m.id)}>
            <h3>{m.title}</h3><p>{m.text}</p>
          </button>
        ))}
        <Card color="white" className="history">
          <div className="row between"><h3>Recent activity</h3>{hist.length > 0 && <button className="linklike" onClick={clear}>Clear</button>}</div>
          {hist.length === 0 ? <p className="muted">Nothing yet. Run an analysis and it shows up here.</p> : (
            <ul className="plain">{hist.slice(0, 5).map((h) => (
              <li key={h.id} className="row gap top"><Badge color="white">{KIND[h.kind] || h.kind}</Badge><span><b>{h.title}</b> <span className="muted">{h.detail}</span></span></li>))}</ul>
          )}
        </Card>
      </div>
    </>
  );
}

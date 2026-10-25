import { useState } from "react";
import { api } from "../api";
import { Badge, Bar, Btn, Card, DemoNote, ErrorBox, List, Loading, MacroDonut, PageHead, Ring, Uploader } from "../components/ui";

export default function Recognition() {
  const [file, setFile] = useState(null);
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const run = async () => {
    setBusy(true); setErr(""); setRes(null);
    try { setRes(await api.nutrition(file)); } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };
  const n = res?.nutrition;

  return (
    <>
      <PageHead color="lemon" title="Food recognition and nutrition" sub="Photograph a meal. Get the dish, the ingredients and a nutrition breakdown with a health score." />
      <div className="grid two">
        <Card>
          <Uploader file={file} onFile={(f) => { setFile(f); setRes(null); }} hint="Drop a meal photo or click to browse" />
          <Btn className="full" disabled={!file || busy} onClick={run}>{busy ? "Analysing..." : "Analyse this meal"}</Btn>
        </Card>
        <div className="stack">
          <ErrorBox message={err} onClose={() => setErr("")} />
          {busy && <Card><Loading text="Identifying dish and estimating nutrition" /></Card>}
          {!res && !busy && !err && <Card color="white" className="placeholder"><h3>Your results land here</h3><p>Upload a photo of a plate, bowl or snack, then press Analyse.</p></Card>}
          {res && (
            <>
              <DemoNote mode={res.mode} />
              <Card color="white">
                <div className="row between wrap">
                  <div>
                    <h2>{res.dish_name}</h2>
                    <div className="row wrap gap"><Badge color="sky">{res.cuisine}</Badge><Badge>{res.portion_size}</Badge>
                      {res.confidence != null && <Badge color="grape">Confidence {Math.round(res.confidence * 100)}%</Badge>}</div>
                  </div>
                  <Ring value={res.health_score} label={res.health_label || "Health"} />
                </div>
              </Card>
              <Card color="white">
                <h3>Nutrition for this portion</h3>
                <div className="kcal"><b>{Math.round(n.calories)}</b> kcal</div>
                <div className="grid two tight">
                  <div>
                    <Bar label="Protein" value={n.protein_g} max={60} color="sky" />
                    <Bar label="Carbohydrates" value={n.carbs_g} max={120} color="lemon" />
                    <Bar label="Fat" value={n.fat_g} max={60} color="tomato" />
                    <Bar label="Fibre" value={n.fiber_g} max={30} color="mint" />
                    <Bar label="Sugar" value={n.sugar_g} max={50} color="grape" />
                    <Bar label="Sodium" value={n.sodium_mg} max={2300} unit="mg" color="white" />
                  </div>
                  <MacroDonut protein={n.protein_g} carbs={n.carbs_g} fat={n.fat_g} />
                </div>
              </Card>
              <div className="grid two">
                <Card color="white"><h3>Ingredients</h3>
                  <ul className="plain">{res.ingredients.map((i, k) => <li key={k}><b>{i.name}</b> <span className="muted">{i.amount}</span></li>)}</ul>
                </Card>
                <Card color={res.allergens.length ? "tomato" : "mint"}><h3>Allergen alerts</h3>
                  {res.allergens.length ? <div className="row wrap gap">{res.allergens.map((a) => <Badge key={a} color="white">{a}</Badge>)}</div> : <p>No common allergens detected.</p>}
                </Card>
              </div>
              <div className="grid two">
                <Card color="white"><h3>What stands out</h3><List items={res.insights} /></Card>
                <Card color="mint"><h3>Make it healthier</h3><List items={res.suggestions} /></Card>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}

import { useState } from "react";
import { api } from "../api";
import { Badge, Btn, Card, DemoNote, ErrorBox, List, Loading, PageHead, Ring, Uploader } from "../components/ui";

const STAGE = { Fresh: "mint", "Moderately Fresh": "lemon", Spoiled: "tomato" };
const SEV = { ok: "mint", warn: "lemon", bad: "tomato" };

export default function Freshness() {
  const [file, setFile] = useState(null);
  const [item, setItem] = useState("");
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const run = async () => {
    setBusy(true); setErr(""); setRes(null);
    try { setRes(await api.freshness(file, item)); } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  return (
    <>
      <PageHead color="mint" title="Freshness and spoilage check" sub="Upload a fruit, vegetable, meat or dairy item. We check colour, texture, wrinkling and mould, then tell you what to do." />
      <div className="grid two">
        <Card>
          <Uploader file={file} onFile={(f) => { setFile(f); setRes(null); }} hint="Drop a photo of the item" />
          <label className="field">What is it? (optional)
            <input value={item} onChange={(e) => setItem(e.target.value)} placeholder="e.g. strawberries, chicken breast" maxLength={60} />
          </label>
          <Btn color="mint" className="full" disabled={!file || busy} onClick={run}>{busy ? "Checking..." : "Check freshness"}</Btn>
        </Card>
        <div className="stack">
          <ErrorBox message={err} onClose={() => setErr("")} />
          {busy && <Card><Loading text="Inspecting surface and colour" /></Card>}
          {!res && !busy && !err && <Card className="placeholder"><h3>Verdict appears here</h3><p>Use good light and a close-up of the item for the best result.</p></Card>}
          {res && (
            <>
              <DemoNote mode={res.mode} />
              <Card color={STAGE[res.stage]}>
                <div className="row between wrap">
                  <div>
                    <h2>{res.stage}</h2>
                    <p className="big">{res.verdict}</p>
                    <div className="row wrap gap"><Badge>{res.item}</Badge><Badge>Shelf life: {res.shelf_life_estimate}</Badge></div>
                  </div>
                  <Ring value={res.freshness_score} label="Fresh" />
                </div>
              </Card>
              <Card>
                <h3>What we saw</h3>
                <ul className="plain">{res.observations.map((o, i) => (
                  <li key={i} className="row gap"><Badge color={SEV[o.severity] || "white"}>{o.factor}</Badge><span>{o.finding}</span></li>
                ))}</ul>
              </Card>
              <Card color="sky"><h3>Storage and safety tips</h3><List items={res.storage_tips} /></Card>
              {res.cv_metrics && (
                <Card>
                  <h3>Image measurements (OpenCV)</h3>
                  <div className="row wrap gap">
                    <Badge>Dark {(res.cv_metrics.dark_ratio * 100).toFixed(1)}%</Badge>
                    <Badge>Brown {(res.cv_metrics.brown_ratio * 100).toFixed(1)}%</Badge>
                    <Badge>Mould-like {(res.cv_metrics.mould_like_ratio * 100).toFixed(1)}%</Badge>
                    <Badge>Texture {res.cv_metrics.texture_variance}</Badge>
                  </div>
                  <p className="muted">Colour analysis is an aid, not a lab test. When in doubt, throw it out.</p>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}

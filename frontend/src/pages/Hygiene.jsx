import { useState } from "react";
import { api } from "../api";
import { Badge, Btn, Card, DemoNote, ErrorBox, Loading, PageHead, Ring, Uploader } from "../components/ui";

const ST = { pass: ["mint", "Pass"], fail: ["tomato", "Fail"], unknown: ["white", "Not visible"] };
const SEV = { critical: "tomato", major: "lemon", minor: "sky" };

export default function Hygiene() {
  const [file, setFile] = useState(null);
  const [res, setRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const run = async () => {
    setBusy(true); setErr(""); setRes(null);
    try { setRes(await api.hygiene(file)); } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  return (
    <>
      <PageHead color="sky" title="Kitchen hygiene audit" sub="Upload a kitchen photo or short video. We check hair covers, gloves, sanitising and cross-contamination, then score compliance." />
      <div className="grid two">
        <Card>
          <Uploader file={file} accept="image/*,video/*" video onFile={(f) => { setFile(f); setRes(null); }} hint="Drop a kitchen photo or video" />
          <Btn color="sky" className="full" disabled={!file || busy} onClick={run}>{busy ? "Auditing..." : "Run hygiene audit"}</Btn>
        </Card>
        <div className="stack">
          <ErrorBox message={err} onClose={() => setErr("")} />
          {busy && <Card><Loading text="Reviewing frames for hygiene indicators" /></Card>}
          {!res && !busy && !err && <Card className="placeholder"><h3>Audit report appears here</h3><p>Videos are sampled into up to 5 frames before analysis.</p></Card>}
          {res && (
            <>
              <DemoNote mode={res.mode} />
              <Card color={res.score >= 85 ? "mint" : res.score >= 60 ? "lemon" : "tomato"}>
                <div className="row between wrap">
                  <div><h2>{res.rating}</h2><p className="big">Compliance score {res.score}%</p>
                    <Badge>{res.frames_analyzed} frame{res.frames_analyzed > 1 ? "s" : ""} analysed</Badge></div>
                  <Ring value={res.score} label="Compliance" />
                </div>
                {res.summary && <p>{res.summary}</p>}
              </Card>
              <Card>
                <h3>Checklist</h3>
                <ul className="plain">{res.indicators.map((i) => (
                  <li key={i.key} className="row gap top"><Badge color={ST[i.status][0]}>{ST[i.status][1]}</Badge>
                    <span><b>{i.label}.</b> {i.detail}</span></li>
                ))}</ul>
              </Card>
              <Card color="white">
                <h3>Violation log</h3>
                {res.violations.length === 0 ? <p>No violations recorded.</p> : (
                  <ul className="plain">{res.violations.map((v, i) => (
                    <li key={i} className="violation"><Badge color={SEV[v.severity] || "white"}>{v.severity}</Badge>
                      <div><b>{v.description}</b><br /><span className="muted">Fix: {v.recommendation}</span></div></li>
                  ))}</ul>
                )}
              </Card>
            </>
          )}
        </div>
      </div>
    </>
  );
}

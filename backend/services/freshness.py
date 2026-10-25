import cv2, numpy as np
from .llm import Creds, ask_json

PROMPT = """You are a food safety inspector. Examine this perishable item{hint}.
Evaluate surface texture, discoloration, wrinkling, bruising, slime, mould and dryness.
Return ONLY JSON:
{{"item": str, "category": "fruit|vegetable|meat|seafood|dairy|bakery|other",
 "stage": "Fresh" | "Moderately Fresh" | "Spoiled", "freshness_score": integer 0-100,
 "observations": [{{"factor": str, "finding": str, "severity": "ok|warn|bad"}}],
 "verdict": "Safe to consume" | "Consume within 24h" | "Discard immediately",
 "storage_tips": [str], "shelf_life_estimate": str, "confidence": number 0-1}}"""

ADVICE = {
    "Fresh": ("Safe to consume", "Several days if stored correctly",
              ["Refrigerate at 1-4 C in a breathable container", "Keep away from raw meat", "Wash only right before use"]),
    "Moderately Fresh": ("Consume within 24h", "Up to 24 hours",
                         ["Use today: cook, blend or freeze right away", "Cut away bruised parts", "Refrigerate until used"]),
    "Spoiled": ("Discard immediately", "Past safe consumption",
                ["Do not taste to check", "Bag and bin it, then wipe the storage area", "Wash hands and any surfaces it touched"]),
}


def cv_metrics(img: bytes) -> dict:
    arr = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
    if arr is None:
        raise ValueError("Could not read the image. Upload a JPG, PNG or WEBP file.")
    h = 480 / max(arr.shape[:2])
    if h < 1:
        arr = cv2.resize(arr, None, fx=h, fy=h)
    hsv = cv2.cvtColor(arr, cv2.COLOR_BGR2HSV)
    H, S, V = cv2.split(hsv)
    total = H.size
    dark = float(np.sum(V < 60)) / total
    brown = float(np.sum((H >= 8) & (H <= 25) & (S > 70) & (V < 150))) / total
    grey_green = float(np.sum((H >= 30) & (H <= 90) & (S < 60) & (V > 60) & (V < 200))) / total
    texture = float(cv2.Laplacian(cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())
    return {"dark_ratio": round(dark, 3), "brown_ratio": round(brown, 3),
            "mould_like_ratio": round(grey_green, 3), "texture_variance": round(texture, 1)}


def _stage(score):
    return "Fresh" if score >= 70 else "Moderately Fresh" if score >= 40 else "Spoiled"


def analyze(img: bytes, mime: str, hint: str, creds: Creds) -> dict:
    m = cv_metrics(img)
    cv_score = int(max(0, min(100, 100 - m["dark_ratio"] * 160 - m["brown_ratio"] * 110 - m["mould_like_ratio"] * 60)))
    if creds.demo:
        stage = _stage(cv_score)
        v, shelf, tips = ADVICE[stage]
        obs = [
            {"factor": "Dark patches", "finding": f"{m['dark_ratio']*100:.1f}% of pixels are very dark", "severity": "ok" if m["dark_ratio"] < .08 else "warn" if m["dark_ratio"] < .2 else "bad"},
            {"factor": "Browning", "finding": f"{m['brown_ratio']*100:.1f}% brown tones", "severity": "ok" if m["brown_ratio"] < .1 else "warn" if m["brown_ratio"] < .25 else "bad"},
            {"factor": "Mould-like tint", "finding": f"{m['mould_like_ratio']*100:.1f}% grey-green tones", "severity": "ok" if m["mould_like_ratio"] < .05 else "warn" if m["mould_like_ratio"] < .15 else "bad"},
        ]
        return {"item": hint or "Perishable item", "category": "other", "stage": stage, "freshness_score": cv_score,
                "observations": obs, "verdict": v, "storage_tips": tips, "shelf_life_estimate": shelf,
                "confidence": 0.45, "cv_metrics": m, "mode": "demo"}
    d = ask_json(PROMPT.format(hint=f" (user says it is: {hint})" if hint else ""), creds, [(img, mime)])
    try:
        d["freshness_score"] = max(0, min(100, int(d.get("freshness_score", cv_score))))
    except (TypeError, ValueError):
        d["freshness_score"] = cv_score
    if d.get("stage") not in ADVICE:
        d["stage"] = _stage(d["freshness_score"])
    v, shelf, tips = ADVICE[d["stage"]]
    d.setdefault("verdict", v); d.setdefault("shelf_life_estimate", shelf)
    d.setdefault("storage_tips", tips); d.setdefault("observations", [])
    d["cv_metrics"] = m; d["mode"] = "live"
    return d

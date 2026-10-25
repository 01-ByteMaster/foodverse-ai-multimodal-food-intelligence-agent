import os, tempfile
import cv2
from .llm import Creds, ask_json

INDICATORS = [("hair_cap", "Hair cap / hairnet"), ("gloves", "Glove usage"), ("sanitization", "Surface sanitisation"),
              ("cross_contamination", "Cross-contamination control"), ("food_handling", "Safe food handling"),
              ("cleanliness", "General cleanliness")]

PROMPT = """You are a food-safety auditor reviewing {n} frame(s) from a commercial kitchen.
Judge each indicator: "pass", "fail" or "unknown" (if not visible). Flag hazards such as raw poultry near vegetables,
bare-hand contact with ready-to-eat food, missing hair covers, dirty surfaces, uncovered food.
Return ONLY JSON:
{{"indicators": [{{"key": one of hair_cap|gloves|sanitization|cross_contamination|food_handling|cleanliness,
   "status": "pass|fail|unknown", "detail": str}}],
 "violations": [{{"severity": "critical|major|minor", "description": str, "recommendation": str}}],
 "summary": str}}"""


def extract_frames(data: bytes, filename: str, max_frames: int = 5) -> list[bytes]:
    """Return JPEG frames. Images pass through; videos are sampled evenly."""
    ext = os.path.splitext(filename or "")[1].lower() or ".mp4"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(data)
        path = f.name
    try:
        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total <= 0:
            raise ValueError("Could not read this video. Try an MP4 or MOV file.")
        frames = []
        for i in range(max_frames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(total * (i + 0.5) / max_frames))
            ok, fr = cap.read()
            if not ok:
                continue
            s = 768 / max(fr.shape[:2])
            if s < 1:
                fr = cv2.resize(fr, None, fx=s, fy=s)
            frames.append(cv2.imencode(".jpg", fr)[1].tobytes())
        cap.release()
        if not frames:
            raise ValueError("No frames could be extracted from the video.")
        return frames
    finally:
        os.unlink(path)


def _score(indicators):
    judged = [i for i in indicators if i["status"] in ("pass", "fail")]
    if not judged:
        return 0
    return round(100 * sum(i["status"] == "pass" for i in judged) / len(judged))


DEMO = {
    "indicators": [
        {"key": "hair_cap", "status": "pass", "detail": "Hairnet visible on the main handler"},
        {"key": "gloves", "status": "fail", "detail": "Bare hands touching ready-to-eat garnish"},
        {"key": "sanitization", "status": "pass", "detail": "Work surface appears wiped and clear"},
        {"key": "cross_contamination", "status": "fail", "detail": "Raw chicken tray stored beside chopped vegetables"},
        {"key": "food_handling", "status": "pass", "detail": "Food kept off the floor, tools in use"},
        {"key": "cleanliness", "status": "pass", "detail": "No visible spills or clutter"},
    ],
    "violations": [
        {"severity": "critical", "description": "Raw poultry placed next to fresh vegetables", "recommendation": "Separate raw proteins; use colour-coded boards and store raw meat on the lowest shelf"},
        {"severity": "major", "description": "Bare-hand contact with ready-to-eat food", "recommendation": "Wear single-use gloves or use tongs for garnish; change gloves between tasks"},
    ],
    "summary": "Sample result. Add an API key to audit your own kitchen footage.",
}


def analyze(data: bytes, filename: str, mime: str, creds: Creds) -> dict:
    is_video = (mime or "").startswith("video") or os.path.splitext(filename or "")[1].lower() in (".mp4", ".mov", ".avi", ".webm", ".mkv")
    frames = extract_frames(data, filename) if is_video else [data]
    if creds.demo:
        d = {k: (list(v) if isinstance(v, list) else v) for k, v in DEMO.items()}
        d["mode"] = "demo"
    else:
        d = ask_json(PROMPT.format(n=len(frames)), creds, [(f, "image/jpeg" if is_video else mime) for f in frames])
        d["mode"] = "live"
    labels = dict(INDICATORS)
    seen = {i.get("key"): i for i in d.get("indicators", [])}
    d["indicators"] = [{"key": k, "label": lbl, "status": seen.get(k, {}).get("status", "unknown"),
                        "detail": seen.get(k, {}).get("detail", "Not visible in the footage")} for k, lbl in INDICATORS]
    d["score"] = _score(d["indicators"])
    d["rating"] = "Compliant" if d["score"] >= 85 else "Needs improvement" if d["score"] >= 60 else "Non-compliant"
    d["frames_analyzed"] = len(frames)
    d.setdefault("violations", []); d.setdefault("summary", "")
    return d

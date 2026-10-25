"""FoodVerse AI - FastAPI backend."""
import os
from pathlib import Path

# Minimal .env loader (no extra dependency). Real environment variables win.
_env = Path(__file__).resolve().parent / ".env"
if _env.is_file():
    for _line in _env.read_text().splitlines():
        if "=" in _line and not _line.strip().startswith("#"):
            _k, _v = _line.split("=", 1)
            if _v.strip():
                os.environ.setdefault(_k.strip(), _v.strip())

from typing import Literal

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from services import freshness, hygiene, mealplan, nutrition, recipes, store
from services.llm import Creds, LLMError

MAX_IMG, MAX_VID = 8 * 1024 * 1024, 40 * 1024 * 1024
app = FastAPI(title="FoodVerse AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
                   allow_methods=["*"], allow_headers=["*"])


async def read_upload(f: UploadFile, kinds: tuple, limit: int) -> bytes:
    if not (f.content_type or "").startswith(kinds):
        raise HTTPException(415, f"Unsupported file type '{f.content_type}'. Expected: {', '.join(kinds)}.")
    data = await f.read()
    if not data:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > limit:
        raise HTTPException(413, f"File too large. Limit is {limit // 1024 // 1024} MB.")
    return data


def guarded(fn, *a):
    try:
        return fn(*a)
    except LLMError as e:
        raise HTTPException(502, str(e))
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.get("/api/health")
def health(x_provider: str | None = Header(None), x_api_key: str | None = Header(None)):
    c = Creds.build(x_provider, x_api_key)
    return {"status": "ok", "mode": "demo" if c.demo else "live", "provider": c.provider}


@app.post("/api/nutrition")
async def api_nutrition(file: UploadFile = File(...), x_provider: str | None = Header(None), x_api_key: str | None = Header(None)):
    img = await read_upload(file, ("image/",), MAX_IMG)
    r = guarded(nutrition.analyze, img, file.content_type, Creds.build(x_provider, x_api_key))
    store.add("nutrition", r["dish_name"], f"{r['nutrition']['calories']} kcal, score {r['health_score']}", r["mode"])
    return r


@app.post("/api/freshness")
async def api_freshness(file: UploadFile = File(...), item: str = Form(""),
                        x_provider: str | None = Header(None), x_api_key: str | None = Header(None)):
    img = await read_upload(file, ("image/",), MAX_IMG)
    r = guarded(freshness.analyze, img, file.content_type, item.strip()[:60], Creds.build(x_provider, x_api_key))
    store.add("freshness", r.get("item", "Item"), f"{r['stage']} ({r['freshness_score']}/100)", r["mode"])
    return r


@app.post("/api/hygiene")
async def api_hygiene(file: UploadFile = File(...), x_provider: str | None = Header(None), x_api_key: str | None = Header(None)):
    data = await read_upload(file, ("image/", "video/"), MAX_VID)
    r = guarded(hygiene.analyze, data, file.filename, file.content_type, Creds.build(x_provider, x_api_key))
    store.add("hygiene", "Kitchen audit", f"{r['score']}% - {r['rating']}", r["mode"])
    return r


class RecipeReq(BaseModel):
    ingredients: list[str] = Field(min_length=1, max_length=30)
    diet: str = "any"
    max_minutes: int = Field(30, ge=5, le=240)
    servings: int = Field(2, ge=1, le=12)


@app.post("/api/recipes")
def api_recipes(req: RecipeReq, x_provider: str | None = Header(None), x_api_key: str | None = Header(None)):
    ings = [i.strip()[:40] for i in req.ingredients if i.strip()]
    if not ings:
        raise HTTPException(422, "Add at least one ingredient.")
    r = guarded(recipes.generate, ings, req.diet, req.max_minutes, req.servings, Creds.build(x_provider, x_api_key))
    store.add("recipes", ", ".join(ings[:3]), f"{len(r['recipes'])} recipes", r["mode"])
    return r


class Profile(BaseModel):
    age: int = Field(ge=14, le=100)
    gender: Literal["male", "female"]
    weight_kg: float = Field(ge=30, le=300)
    height_cm: float = Field(ge=120, le=230)
    activity: Literal["sedentary", "light", "moderate", "active", "athlete"]
    goal: Literal["fat_loss", "maintain", "muscle_gain"]
    diet: Literal["standard", "vegetarian", "vegan", "keto", "diabetic"]
    allergies: str = ""


@app.post("/api/mealplan")
def api_mealplan(p: Profile, x_provider: str | None = Header(None), x_api_key: str | None = Header(None)):
    r = guarded(mealplan.generate, p.model_dump(), Creds.build(x_provider, x_api_key))
    store.add("mealplan", f"{p.goal.replace('_', ' ')} / {p.diet}", f"{r['targets']['calories']} kcal per day", r["mode"])
    return r


@app.get("/api/history")
def history():
    return store.list_all()


@app.delete("/api/history")
def clear_history():
    store.clear()
    return {"ok": True}


# Serve the built React app when present (single-service deployment)
DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        f = DIST / path
        return FileResponse(f if path and f.is_file() else DIST / "index.html")

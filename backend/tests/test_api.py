"""Run from backend/:  pip install pytest && pytest -q"""
import cv2, numpy as np
from fastapi.testclient import TestClient
from main import app

c = TestClient(app)
IMG = cv2.imencode(".jpg", np.full((200, 200, 3), (40, 90, 140), np.uint8))[1].tobytes()
F = {"file": ("a.jpg", IMG, "image/jpeg")}


def test_health_demo(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert c.get("/api/health").json()["mode"] == "demo"

def test_nutrition():
    r = c.post("/api/nutrition", files=F); assert r.status_code == 200 and 1 <= r.json()["health_score"] <= 100

def test_freshness():
    assert c.post("/api/freshness", files=F, data={"item": "apple"}).json()["stage"] in ("Fresh", "Moderately Fresh", "Spoiled")

def test_hygiene():
    assert 0 <= c.post("/api/hygiene", files=F).json()["score"] <= 100

def test_recipes():
    assert c.post("/api/recipes", json={"ingredients": ["egg"]}).json()["recipes"]

def test_mealplan_targets():
    p = dict(age=30, gender="female", weight_kg=60, height_cm=165, activity="light", goal="fat_loss", diet="vegan")
    j = c.post("/api/mealplan", json=p).json()
    assert len(j["days"]) == 7 and j["targets"]["calories"] >= 1200

def test_bad_upload():
    assert c.post("/api/nutrition", files={"file": ("a.txt", b"x", "text/plain")}).status_code == 415

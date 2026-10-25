import hashlib
from .llm import Creds, ask_json

PROMPT = """You are an expert food scientist and dietitian. Analyse this meal photo.
Return ONLY JSON with this exact shape:
{"dish_name": str, "cuisine": str, "portion_size": str,
 "ingredients": [{"name": str, "amount": str}],
 "nutrition": {"calories": number, "protein_g": number, "carbs_g": number, "fat_g": number,
               "fiber_g": number, "sugar_g": number, "sodium_mg": number},
 "allergens": [str], "health_score": integer 1-100, "health_label": str,
 "insights": [str], "suggestions": [str], "confidence": number 0-1}
Estimate for the visible portion. If the image is not food, set dish_name to "Not food" and calories to 0."""

DEMO = [
    {"dish_name": "Chicken Biryani", "cuisine": "Indian", "portion_size": "1 plate (~350 g)",
     "ingredients": [{"name": "Basmati rice", "amount": "200 g"}, {"name": "Chicken thigh", "amount": "120 g"},
                     {"name": "Fried onion", "amount": "15 g"}, {"name": "Ghee and spices", "amount": "10 g"}],
     "nutrition": {"calories": 620, "protein_g": 32, "carbs_g": 78, "fat_g": 18, "fiber_g": 3, "sugar_g": 4, "sodium_mg": 880},
     "allergens": ["Dairy (ghee)"], "health_score": 58, "health_label": "Moderate",
     "insights": ["High in carbohydrates from rice", "Good protein content", "Sodium is on the high side"],
     "suggestions": ["Add a cucumber raita or salad for fibre", "Halve the rice portion and add vegetables"], "confidence": 0.8},
    {"dish_name": "Greek Salad Bowl", "cuisine": "Mediterranean", "portion_size": "1 bowl (~300 g)",
     "ingredients": [{"name": "Tomato", "amount": "100 g"}, {"name": "Cucumber", "amount": "80 g"},
                     {"name": "Feta", "amount": "40 g"}, {"name": "Olives", "amount": "30 g"}, {"name": "Olive oil", "amount": "10 ml"}],
     "nutrition": {"calories": 280, "protein_g": 9, "carbs_g": 14, "fat_g": 22, "fiber_g": 4, "sugar_g": 8, "sodium_mg": 720},
     "allergens": ["Dairy (feta)"], "health_score": 84, "health_label": "Excellent",
     "insights": ["Rich in healthy monounsaturated fats", "Low in refined carbs"],
     "suggestions": ["Add chickpeas or grilled chicken to raise protein"], "confidence": 0.85},
    {"dish_name": "Margherita Pizza (2 slices)", "cuisine": "Italian", "portion_size": "2 slices (~200 g)",
     "ingredients": [{"name": "Wheat dough", "amount": "120 g"}, {"name": "Mozzarella", "amount": "60 g"},
                     {"name": "Tomato sauce", "amount": "40 g"}, {"name": "Basil", "amount": "2 g"}],
     "nutrition": {"calories": 540, "protein_g": 22, "carbs_g": 66, "fat_g": 20, "fiber_g": 3, "sugar_g": 6, "sodium_mg": 980},
     "allergens": ["Gluten", "Dairy"], "health_score": 52, "health_label": "Moderate",
     "insights": ["Refined flour base raises glycaemic load", "Decent calcium from cheese"],
     "suggestions": ["Pair with a green salad", "Choose a whole wheat base"], "confidence": 0.8},
]


def _clamp(d):
    n = d.setdefault("nutrition", {})
    for k in ("calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "sugar_g", "sodium_mg"):
        try:
            n[k] = round(float(n.get(k, 0)), 1)
        except (TypeError, ValueError):
            n[k] = 0
    try:
        d["health_score"] = max(1, min(100, int(d.get("health_score", 50))))
    except (TypeError, ValueError):
        d["health_score"] = 50
    for k in ("ingredients", "allergens", "insights", "suggestions"):
        d.setdefault(k, [])
    return d


def analyze(img: bytes, mime: str, creds: Creds) -> dict:
    if creds.demo:
        d = dict(DEMO[int(hashlib.md5(img).hexdigest(), 16) % len(DEMO)])
        d["mode"] = "demo"
        return _clamp(d)
    d = _clamp(ask_json(PROMPT, creds, [(img, mime)]))
    d["mode"] = "live"
    return d

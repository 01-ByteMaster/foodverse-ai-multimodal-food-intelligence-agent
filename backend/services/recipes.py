from .llm import Creds, ask_json

PROMPT = """You are a creative chef and nutritionist. The user has these pantry ingredients: {ing}.
Diet: {diet}. Max cooking time: {mins} minutes. Servings: {serv}.
Create {n} different recipes using mostly these ingredients (assume salt, pepper, oil, water).
Return ONLY JSON:
{{"recipes": [{{"name": str, "cook_time_min": int, "difficulty": "Easy|Medium|Hard", "servings": int,
 "calories_per_serving": int, "protein_g": int,
 "ingredients": [{{"item": str, "amount": str, "have": boolean}}],
 "substitutions": [{{"missing": str, "alternative": str}}],
 "steps": [str], "tip": str}}]}}"""


def _demo(ings, diet, mins, serv):
    a = ings[0].title(); b = ings[1].title() if len(ings) > 1 else "Seasonal Veg"
    rest = ings[2:5]
    items = [{"item": i, "amount": "as needed", "have": True} for i in ings[:6]]
    return {"recipes": [
        {"name": f"One-Pan {a} and {b} Skillet", "cook_time_min": min(25, mins), "difficulty": "Easy", "servings": serv,
         "calories_per_serving": 420, "protein_g": 22, "ingredients": items + [{"item": "Olive oil", "amount": "1 tbsp", "have": False}],
         "substitutions": [{"missing": "Olive oil", "alternative": "Any neutral oil or butter"}],
         "steps": ["Chop everything into bite-sized pieces.", f"Heat oil in a wide pan and sear {a.lower()} for 4 minutes.",
                   f"Add {b.lower()}{' and ' + ', '.join(rest) if rest else ''}; cook 8 minutes, stirring.",
                   "Season, taste, and serve hot."], "tip": "High heat and a dry pan give better browning."},
        {"name": f"{b} Power Bowl", "cook_time_min": min(15, mins), "difficulty": "Easy", "servings": serv,
         "calories_per_serving": 360, "protein_g": 16, "ingredients": items[:4],
         "substitutions": [{"missing": "Grains", "alternative": "Rice, quinoa or toasted bread"}],
         "steps": ["Cook or warm your base.", f"Top with {a.lower()} and {b.lower()}.", "Finish with lemon, herbs and a pinch of salt."],
         "tip": "Prep toppings in advance for quick lunches."}],
        "mode": "demo"}


def generate(ings, diet, mins, serv, creds: Creds):
    if creds.demo:
        return _demo(ings, diet, mins, serv)
    d = ask_json(PROMPT.format(ing=", ".join(ings), diet=diet, mins=mins, serv=serv, n=3), creds)
    d.setdefault("recipes", []); d["mode"] = "live"
    return d

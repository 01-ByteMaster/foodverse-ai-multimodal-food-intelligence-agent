"""Deterministic BMR/TDEE maths + 7-day plan (LLM-generated or built-in demo library)."""
from .llm import Creds, ask_json

ACTIVITY = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "athlete": 1.9}
GOAL_ADJ = {"fat_loss": -0.20, "maintain": 0.0, "muscle_gain": 0.10}
# (protein, carbs, fat) share of calories
SPLIT = {"standard": (.25, .45, .30), "vegetarian": (.22, .50, .28), "vegan": (.20, .55, .25),
         "keto": (.25, .05, .70), "diabetic": (.25, .40, .35)}
GOAL_PROTEIN_BONUS = {"muscle_gain": .05, "fat_loss": .03, "maintain": 0}
SHARES = [("Breakfast", .25), ("Lunch", .35), ("Dinner", .30), ("Snack", .10)]


def targets(p: dict) -> dict:
    w, h, a = float(p["weight_kg"]), float(p["height_cm"]), int(p["age"])
    bmr = 10 * w + 6.25 * h - 5 * a + (5 if p["gender"] == "male" else -161)
    tdee = bmr * ACTIVITY[p["activity"]]
    cal = max(1200 if p["gender"] == "female" else 1500, tdee * (1 + GOAL_ADJ[p["goal"]]))
    pr, cr, ft = SPLIT[p["diet"]]
    bonus = GOAL_PROTEIN_BONUS[p["goal"]]
    pr += bonus
    if p["diet"] == "keto":
        ft -= bonus
    else:
        cr -= bonus
    return {"bmr": round(bmr), "tdee": round(tdee), "calories": round(cal),
            "protein_g": round(cal * pr / 4), "carbs_g": round(cal * cr / 4), "fat_g": round(cal * ft / 9),
            "bmi": round(w / (h / 100) ** 2, 1)}


L = {
 "standard": {
  "Breakfast": [("Veg omelette with toast", 380, ["eggs", "bell pepper", "spinach", "whole wheat bread"]),
                ("Greek yogurt with berries and oats", 340, ["greek yogurt", "mixed berries", "rolled oats", "honey"]),
                ("Poha with peanuts", 360, ["flattened rice", "peanuts", "onion", "lemon"])],
  "Lunch": [("Grilled chicken rice bowl", 560, ["chicken breast", "brown rice", "broccoli", "olive oil"]),
            ("Dal, roti and cucumber salad", 520, ["lentils", "whole wheat flour", "cucumber", "tomato"]),
            ("Tuna and chickpea salad wrap", 500, ["canned tuna", "chickpeas", "tortilla wraps", "lettuce"])],
  "Dinner": [("Baked fish with roasted vegetables", 480, ["white fish fillet", "zucchini", "carrot", "olive oil"]),
             ("Paneer tikka with salad", 500, ["paneer", "yogurt", "onion", "bell pepper"]),
             ("Chicken stir-fry with noodles", 540, ["chicken breast", "noodles", "cabbage", "soy sauce"])],
  "Snack": [("Apple with peanut butter", 220, ["apple", "peanut butter"]), ("Roasted chana", 180, ["chickpeas"])]},
 "vegetarian": {
  "Breakfast": [("Besan chilla with mint chutney", 340, ["gram flour", "onion", "mint", "tomato"]),
                ("Overnight oats with banana", 360, ["rolled oats", "milk", "banana", "chia seeds"]),
                ("Paneer bhurji toast", 380, ["paneer", "whole wheat bread", "tomato", "onion"])],
  "Lunch": [("Rajma, brown rice and salad", 540, ["kidney beans", "brown rice", "cucumber", "tomato"]),
            ("Paneer and veg quinoa bowl", 520, ["paneer", "quinoa", "broccoli", "carrot"]),
            ("Vegetable khichdi with curd", 480, ["lentils", "rice", "mixed vegetables", "yogurt"])],
  "Dinner": [("Palak paneer with roti", 520, ["spinach", "paneer", "whole wheat flour", "onion"]),
             ("Lentil soup with grilled veg sandwich", 480, ["lentils", "whole wheat bread", "zucchini", "cheese"]),
             ("Tofu stir-fry with brown rice", 500, ["tofu", "brown rice", "bell pepper", "soy sauce"])],
  "Snack": [("Fruit and nut mix", 200, ["almonds", "apple"]), ("Sprouts chaat", 170, ["sprouts", "onion", "lemon"])]},
 "vegan": {
  "Breakfast": [("Tofu scramble with toast", 360, ["tofu", "turmeric", "whole wheat bread", "spinach"]),
                ("Chia pudding with mango", 330, ["chia seeds", "soy milk", "mango"]),
                ("Peanut butter banana oats", 380, ["rolled oats", "peanut butter", "banana", "soy milk"])],
  "Lunch": [("Chickpea curry with brown rice", 540, ["chickpeas", "brown rice", "tomato", "onion"]),
            ("Quinoa black bean bowl", 520, ["quinoa", "black beans", "corn", "avocado"]),
            ("Lentil and veg soup with bread", 480, ["lentils", "carrot", "whole wheat bread", "celery"])],
  "Dinner": [("Tofu and broccoli stir-fry", 480, ["tofu", "broccoli", "soy sauce", "brown rice"]),
             ("Vegetable dal with roti", 500, ["lentils", "whole wheat flour", "spinach", "tomato"]),
             ("Stuffed bell peppers with rice", 490, ["bell pepper", "rice", "kidney beans", "tomato"])],
  "Snack": [("Hummus with carrot sticks", 200, ["hummus", "carrot"]), ("Roasted peanuts", 190, ["peanuts"])]},
 "keto": {
  "Breakfast": [("Cheese and spinach omelette", 420, ["eggs", "cheese", "spinach", "butter"]),
                ("Avocado and egg plate", 400, ["avocado", "eggs", "olive oil"]),
                ("Chia coconut pudding", 360, ["chia seeds", "coconut milk", "almonds"])],
  "Lunch": [("Chicken Caesar salad (no croutons)", 520, ["chicken breast", "lettuce", "parmesan", "olive oil"]),
            ("Paneer tikka with sauteed greens", 540, ["paneer", "spinach", "butter", "bell pepper"]),
            ("Tuna-stuffed avocado", 480, ["canned tuna", "avocado", "mayonnaise"])],
  "Dinner": [("Salmon with asparagus", 560, ["salmon fillet", "asparagus", "butter", "lemon"]),
             ("Zucchini noodles with pesto chicken", 520, ["zucchini", "chicken breast", "pesto", "parmesan"]),
             ("Egg curry with cauliflower rice", 500, ["eggs", "cauliflower", "onion", "coconut milk"])],
  "Snack": [("Almonds and cheese cubes", 210, ["almonds", "cheese"]), ("Boiled eggs", 160, ["eggs"])]},
 "diabetic": {
  "Breakfast": [("Moong dal chilla", 320, ["moong dal", "onion", "mint", "tomato"]),
                ("Veg oats upma", 330, ["rolled oats", "mixed vegetables", "mustard seeds"]),
                ("Egg whites with multigrain toast", 340, ["eggs", "multigrain bread", "spinach"])],
  "Lunch": [("Grilled chicken with quinoa and greens", 520, ["chicken breast", "quinoa", "lettuce", "cucumber"]),
            ("Methi roti, dal and salad", 500, ["fenugreek leaves", "whole wheat flour", "lentils", "cucumber"]),
            ("Chickpea salad bowl", 480, ["chickpeas", "tomato", "cucumber", "olive oil"])],
  "Dinner": [("Baked fish with sauteed vegetables", 470, ["white fish fillet", "broccoli", "carrot", "olive oil"]),
             ("Paneer and vegetable stir-fry", 490, ["paneer", "bell pepper", "cabbage", "onion"]),
             ("Vegetable soup with grilled tofu", 430, ["tofu", "mixed vegetables", "celery"])],
  "Snack": [("Handful of almonds", 170, ["almonds"]), ("Cucumber and hummus", 150, ["cucumber", "hummus"])]},
}

CATS = {"Produce": ["pepper", "spinach", "onion", "lemon", "berries", "apple", "banana", "tomato", "cucumber", "broccoli", "carrot",
                    "zucchini", "cabbage", "lettuce", "mint", "avocado", "mango", "asparagus", "cauliflower", "celery", "corn",
                    "fenugreek", "vegetables", "sprouts"],
        "Protein": ["eggs", "chicken", "tuna", "fish", "paneer", "tofu", "salmon"],
        "Dairy": ["yogurt", "milk", "cheese", "butter", "parmesan", "curd"],
        "Grains and bread": ["bread", "rice", "oats", "flour", "tortilla", "quinoa", "noodles", "flattened"],
        "Pantry": []}


def _cat(item):
    for c, keys in CATS.items():
        if any(k in item for k in keys):
            return c
    return "Pantry"


def demo_plan(t: dict, diet: str) -> dict:
    lib = L[diet]
    days, grocery = [], {}
    pr, cr, ft = SPLIT[diet]
    for d in range(7):
        meals = []
        for name, share in SHARES:
            opts = lib[name]
            title, base, items = opts[d % len(opts)] if name != "Snack" else opts[d % 2]
            kcal = round(t["calories"] * share)
            scale = kcal / base
            meals.append({"type": name, "name": title, "calories": kcal, "portion": f"x{scale:.2f} of base serving",
                          "protein_g": round(kcal * pr / 4), "carbs_g": round(kcal * cr / 4), "fat_g": round(kcal * ft / 9),
                          "items": items})
            for it in items:
                grocery.setdefault(_cat(it), {}); grocery[_cat(it)][it] = grocery[_cat(it)].get(it, 0) + 1
        days.append({"day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][d], "meals": meals,
                     "total_calories": sum(m["calories"] for m in meals)})
    g = {c: [f"{k} (used in {v} meals)" if v > 1 else k for k, v in sorted(items.items())] for c, items in grocery.items()}
    return {"days": days, "grocery": g}


PROMPT = """You are a registered dietitian. Create a 7-day meal plan.
Daily targets: {calories} kcal, {protein_g} g protein, {carbs_g} g carbs, {fat_g} g fat.
Profile: {age}y {gender}, goal {goal}, diet {diet}. Allergies/dislikes: {allergies}.
Use 4 meals per day: Breakfast, Lunch, Dinner, Snack. Each day should land within 5% of the calorie target.
Return ONLY JSON:
{{"days": [{{"day": "Monday", "meals": [{{"type": str, "name": str, "calories": int, "protein_g": int, "carbs_g": int,
  "fat_g": int, "portion": str, "items": [str]}}]}}],
 "grocery": {{"Produce": [str], "Protein": [str], "Dairy": [str], "Grains and bread": [str], "Pantry": [str]}},
 "notes": [str]}}"""


def generate(p: dict, creds: Creds) -> dict:
    t = targets(p)
    if creds.demo:
        plan = demo_plan(t, p["diet"]); plan["mode"] = "demo"
    else:
        plan = ask_json(PROMPT.format(**t, age=p["age"], gender=p["gender"], goal=p["goal"], diet=p["diet"],
                                      allergies=p.get("allergies") or "none"), creds)
        plan["mode"] = "live"
        for d in plan.get("days", []):
            d["total_calories"] = sum(int(m.get("calories", 0)) for m in d.get("meals", []))
        plan.setdefault("grocery", {})
    plan["targets"] = t
    return plan

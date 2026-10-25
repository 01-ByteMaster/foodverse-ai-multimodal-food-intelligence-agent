# FoodVerse AI - Multimodal Food Intelligence Agent

React + FastAPI platform for food recognition and nutrition, freshness detection, kitchen hygiene audits,
a recipe assistant and personalised 7-day meal plans. Neobrutalist UI. Works with no key (demo mode) or with
Google Gemini / Groq keys for live multimodal AI.

Quick start:

    # terminal 1
    cd backend && python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt && uvicorn main:app --reload --port 8000
    # terminal 2
    cd frontend && npm install && npm run dev      # open http://localhost:5173

Full instructions, deployment and troubleshooting: see WALKTHROUGH.md

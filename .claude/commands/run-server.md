---
description: Start the Dino FastAPI backend and open the frontend for local development.
---

Run the following steps:

1. Check that `.env` exists and contains `GOOGLE_MAPS_API_KEY` and `ANTHROPIC_API_KEY`
2. Start the FastAPI server: `uvicorn src.api.main:app --reload --port 8000`
3. Report the URL: `http://localhost:8000` (API) and `http://localhost:8000/docs` (auto-generated docs)
4. If `frontend/index.html` exists, suggest opening it in a browser

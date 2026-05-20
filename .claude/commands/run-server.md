---
description: Start the Dino FastAPI backend and open the frontend for local development.
---

Run the following steps:

1. Check that `.env` exists and contains `GOOGLE_MAPS_API_KEY` and `ANTHROPIC_API_KEY`. If either is missing, warn the user before continuing.
2. Activate the venv: `source ~/Dropbox/ai-projects/venv-dino/bin/activate`
3. Start the FastAPI server in the background: `uvicorn src.api.main:app --reload --port 8000`
4. Open the frontend in the default browser: `open frontend/index.html`
5. Report: API at `http://localhost:8000`, docs at `http://localhost:8000/docs`, frontend opened in browser.

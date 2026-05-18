# Dino — AI Vegas Dining Concierge

## What this project is

Dino is a conversational AI dining concierge for Las Vegas. Named after Dean Martin, with Rat Pack-era charm. Users chat with Dino in a mobile-first web UI. Dino recommends restaurants from real Google Maps data, checks availability, books tables, and adds confirmations to Google Calendar.

## Architecture

```
Chat UI (HTML/CSS/JS) → FastAPI backend → Dino Agent (Claude Sonnet) → Tools
```

The backend is the product. The frontend is a thin client that calls `POST /chat`.

### Key directories

- `src/agent/` — Dino's brain: system prompt, tool definitions, agent loop
- `src/services/` — External integrations: Google Maps Places, mock booking, Google Calendar
- `src/data/` — Curated Vegas restaurant dataset and mock availability
- `src/api/` — FastAPI application
- `frontend/` — Standalone HTML/CSS/JS chat UI
- `.claude/skills/` — Claude Code skills for this project

### Tools the agent uses

| Tool | Source | Real/Mock |
|------|--------|-----------|
| `search_restaurants` | Google Maps Places API | Real |
| `get_restaurant_details` | Google Maps Places API | Real |
| `check_availability` | Mock booking service | Mock |
| `create_reservation` | Mock booking service | Mock |
| `add_to_calendar` | Google Calendar API | Real |
| `get_booking_link` | URL builder | Real (deep links) |

## Code conventions

- Python 3.12+, type hints on all function signatures
- Use `httpx` for async HTTP calls (not `requests`)
- Use `pydantic` for data models and API schemas
- 4-space indentation, double quotes for strings
- Descriptive variable names, no abbreviations
- Each file under 300 lines. If it's longer, split it.
- Environment variables for all secrets: `GOOGLE_MAPS_API_KEY`, `ANTHROPIC_API_KEY`
- Load env vars with `python-dotenv` from a `.env` file (gitignored)

## Environment

- Venv: `source ~/Dropbox/ai-projects/venv-dino/bin/activate`
- Venv activation is per-session — always activate before running anything

## Testing

- Run tests: `python -m pytest tests/`
- Run the API locally: `uvicorn src.api.main:app --reload --port 8000`
- Test a chat turn: `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "Best Italian near the Strip", "conversation_id": "test-1"}'`

## Key decisions

1. **Mock booking with real interface.** `src/services/booking.py` mirrors a real reservation API contract. The agent doesn't know it's a mock. Swapping in a real provider (SevenRooms, Yelp) means changing the service implementation, not the agent or tools.
2. **Personality lives in the system prompt.** `src/agent/personality.py` builds Dino's system prompt. All voice, tone, and behavioral rules are prompt engineering. No special personality module or post-processing.
3. **Structured responses.** The `/chat` endpoint returns both Dino's text and structured data (restaurant cards, booking confirmations). The frontend renders structured data as rich UI components.
4. **No database for v1.** Conversations stored in memory. Persistence is a Week 14 concern.

## Dino's voice (quick reference)

- Warm, confident, opinionated but not pushy
- Recommends with reasons, doesn't list options neutrally
- Knows Vegas dining cold — has favorites, shares insider tips
- Never uses corporate language, sales pressure, or fake urgency
- Handles "I don't know what I want" gracefully — asks about vibe, not cuisine
- See `.claude/skills/dino-personality/SKILL.md` for full voice guidelines

## What NOT to do

- Don't add a database or auth system — v1 is stateless
- Don't build an admin panel — this is a consumer product
- Don't use React or any JS framework for the frontend — vanilla HTML/CSS/JS only
- Don't hardcode API keys anywhere — always use environment variables
- Don't make Dino a search engine — he's a concierge with opinions

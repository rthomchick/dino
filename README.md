# Dino — AI Vegas Dining Concierge

A conversational AI dining concierge for Las Vegas. Named after Dean Martin, with Rat Pack-era charm. Dino recommends restaurants, checks availability, books tables, and adds reservations to Google Calendar with insider tips.

**Live:** [web-production-c0565.up.railway.app](https://web-production-c0565.up.railway.app)

## What Dino does

Tell Dino what kind of night you're planning. He recommends restaurants with strong opinions, checks availability, books a table, and adds the reservation to your Google Calendar — complete with an insider tip about what to order or where to sit.

Dino orchestrates six tools through a single-agent tool loop:

| Tool | Source | Status |
|------|--------|--------|
| `search_restaurants` | Google Maps Places API | Real |
| `get_restaurant_details` | Google Maps Places API | Real |
| `check_availability` | Booking service | Mock |
| `create_reservation` | Booking service | Mock |
| `add_to_calendar` | Google Calendar deep links | Real |
| `get_booking_link` | URL builder | Real |

The booking service uses a mock implementation with a real API contract. The agent doesn't know it's a mock. Swapping in a real provider means changing the service, not the agent.

## Architecture

```
Chat UI (HTML/CSS/JS) → FastAPI backend → Dino Agent (Claude Sonnet) → Tools
```

The backend is the product. The frontend is a thin client that calls `POST /chat`.

## Project structure

```
dino/
├── src/
│   ├── agent/
│   │   ├── dino.py              # Agent loop + tool orchestration
│   │   ├── personality.py       # System prompt + Dino's voice
│   │   └── tools.py             # Tool definitions
│   ├── services/
│   │   ├── places.py            # Google Maps Places API
│   │   ├── booking.py           # Mock booking (real contract)
│   │   └── calendar.py          # Google Calendar deep links
│   ├── data/                    # Curated restaurant data
│   └── api/
│       ├── main.py              # FastAPI app
│       └── models.py            # Pydantic response models
├── frontend/
│   └── index.html               # Chat UI (vanilla HTML/CSS/JS)
├── tests/
├── .claude/
│   ├── commands/                # Claude Code slash commands
│   └── skills/                  # Claude Code skill files
├── CLAUDE.md                    # Claude Code project context
├── Procfile                     # Railway start command
├── requirements.txt
└── .env.example
```

## Setup

### Prerequisites

- Python 3.12+
- [Anthropic API key](https://console.anthropic.com/)
- [Google Maps API key](https://console.cloud.google.com/) with Places API enabled

### Install

```bash
git clone https://github.com/rthomchick/dino.git
cd dino
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

Copy `.env.example` to `.env` and add your keys:

```
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_MAPS_API_KEY=AIza...
```

### Run

```bash
uvicorn src.api.main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000).

## Deployment

Deployed on [Railway](https://railway.com) (Hobby plan, $5/month). Railway auto-deploys from the `main` branch on push.

Required environment variables in Railway:
- `ANTHROPIC_API_KEY`
- `GOOGLE_MAPS_API_KEY`

## Tech stack

- **Backend:** Python, FastAPI, httpx, Pydantic
- **AI:** Anthropic API (Claude Sonnet)
- **Discovery:** Google Maps Places API
- **Calendar:** Google Calendar deep links
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Hosting:** Railway

## Built by

Richard Thomchick — [richardthomchick.com](https://richardthomchick.com)

Built during Week 13 of an AI Product Development Program. Part of a portfolio of AI-powered tools built by a PM learning to ship AI products.

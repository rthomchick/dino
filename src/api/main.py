import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.agent.dino import DinoAgent, _load_curated
from src.api.models import (
    ChatRequest,
    ChatResponse,
    ConversationMessage,
    ConversationResponse,
    HealthResponse,
)

# Resolve .env relative to this file so it loads regardless of working directory
_ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_ENV_PATH, override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VERSION = "0.1.0"

agent: DinoAgent


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    agent = DinoAgent()
    curated = _load_curated()
    logger.info(f"Dino is open for business — {len(curated)} curated restaurants loaded")
    yield


app = FastAPI(
    title="Dino — AI Vegas Dining Concierge",
    version=VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to known origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version=VERSION)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Append guest name to message when provided and not already embedded
    message = request.message
    if request.guest_name and request.guest_name.lower() not in message.lower():
        message = f"{message} (guest name: {request.guest_name})"

    try:
        response = await agent.chat(message, conversation_id)
    except anthropic.APIError:
        raise HTTPException(
            status_code=502,
            detail="The kitchen's backed up, pal. Give me a second and try again.",
        )

    return ChatResponse(
        message=response.message,
        conversation_id=conversation_id,
        restaurant_cards=response.restaurant_cards,
        booking_confirmation=response.booking_confirmation,
        calendar_event=response.calendar_event,
    )


_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")


@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(_FRONTEND_DIR, "index.html"))


@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    history = agent.conversations.get(conversation_id)
    if history is None:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id!r} not found")

    messages = []
    for entry in history:
        role = entry["role"]
        content = entry["content"]

        if isinstance(content, str):
            messages.append(ConversationMessage(role=role, content=content))
        elif isinstance(content, list):
            # Flatten content blocks (text blocks from assistant turns, tool results from user turns)
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block["content"])
                    elif block.get("type") == "tool_result":
                        text_parts.append(f"[tool_result: {block.get('tool_use_id', '')}]")
                elif hasattr(block, "type"):
                    if block.type == "text":
                        text_parts.append(block.text)
                    elif block.type == "tool_use":
                        text_parts.append(f"[tool_use: {block.name}]")
            if text_parts:
                messages.append(ConversationMessage(role=role, content=" ".join(text_parts)))

    return ConversationResponse(
        conversation_id=conversation_id,
        messages=messages,
        turn_count=sum(1 for m in messages if m.role == "user"),
    )


app.mount("/static", StaticFiles(directory=_FRONTEND_DIR), name="static")

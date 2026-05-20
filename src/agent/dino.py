import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
import anthropic
from pydantic import BaseModel

from src.agent.personality import build_system_prompt
from src.agent.tools import TOOLS
from src.services import places, booking

_DATA_PATH = Path(__file__).parent.parent / "data" / "vegas_restaurants.json"
_curated_cache: Optional[dict] = None

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048


class AgentResponse(BaseModel):
    message: str
    restaurant_cards: Optional[list[dict]] = None
    booking_confirmation: Optional[dict] = None
    calendar_event: Optional[dict] = None
    conversation_id: str


def _load_curated() -> dict:
    global _curated_cache
    if _curated_cache is None:
        with open(_DATA_PATH) as f:
            restaurants = json.load(f)
        _curated_cache = {r["venue_id"]: r for r in restaurants}
    return _curated_cache


def _enrich_with_curated(restaurants: list, curated: dict) -> list[dict]:
    """Merge Places API results with curated dataset — venue_id match by name."""
    curated_by_name = {v["name"].lower(): v for v in curated.values()}
    enriched = []
    for r in restaurants:
        data = r.model_dump()
        match = curated_by_name.get(r.name.lower())
        if match:
            data["venue_id"] = match["venue_id"]
            data["dino_take"] = match.get("dino_take")
            data["bookable"] = match.get("bookable", False)
            data["booking_url"] = match.get("booking_url")
        else:
            data["venue_id"] = None
            data["bookable"] = False
        enriched.append(data)
    return enriched


def _build_calendar_link(
    restaurant_name: str,
    location: str,
    address: str,
    date: str,
    time: str,
    party_size: int,
    confirmation_number: str,
    insider_tip: str = "",
) -> dict:
    start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(hours=2)
    fmt = "%Y%m%dT%H%M%S"
    description_parts = [
        f"Party of {party_size}",
        f"Confirmation: {confirmation_number}",
    ]
    if insider_tip:
        description_parts.append(f"\nDino's insider tip: {insider_tip}")
    description_parts.append("\nBooked via Dino — your Vegas dining concierge")
    full_location = f"{restaurant_name}, {address}" if address else f"{restaurant_name}, {location}"
    params = {
        "action": "TEMPLATE",
        "text": f"Dinner at {restaurant_name}",
        "dates": f"{start_dt.strftime(fmt)}/{end_dt.strftime(fmt)}",
        "location": full_location,
        "details": "\n".join(description_parts),
    }
    return {
        "calendar_url": f"https://calendar.google.com/calendar/render?{urlencode(params)}",
        "title": f"Dinner at {restaurant_name}",
        "start": f"{date}T{time}",
        "location": full_location,
        "status": "link_generated",
    }


def _parse_structured_blocks(text: str) -> tuple[str, list[dict], Optional[dict], Optional[dict]]:
    """Extract [RESTAURANT_CARD], [BOOKING_CONFIRMED], [CALENDAR_ADDED] blocks from text."""
    restaurant_cards = []
    booking_confirmation = None
    calendar_event = None

    def extract(tag: str, content: str) -> tuple[list[dict], str]:
        pattern = rf"\[{tag}\]\s*(.*?)\s*\[/{tag}\]"
        matches = re.findall(pattern, content, re.DOTALL)
        parsed = []
        for m in matches:
            try:
                parsed.append(json.loads(m.strip()))
            except json.JSONDecodeError:
                pass
        cleaned = re.sub(pattern, "", content, flags=re.DOTALL)
        # Collapse multiple blank lines left behind by block removal
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        return parsed, cleaned

    cards, text = extract("RESTAURANT_CARD", text)
    restaurant_cards.extend(cards)

    bookings, text = extract("BOOKING_CONFIRMED", text)
    if bookings:
        booking_confirmation = bookings[0]

    calendars, text = extract("CALENDAR_EVENT", text)
    if calendars:
        calendar_event = calendars[0]

    return text.strip(), restaurant_cards or None, booking_confirmation, calendar_event


async def _execute_tool(tool_name: str, tool_input: dict) -> str:
    curated = _load_curated()

    if tool_name == "search_restaurants":
        results = await places.search_restaurants(
            query=tool_input["query"],
            cuisine_type=tool_input.get("cuisine_type"),
            price_level=tool_input.get("price_level"),
            max_results=tool_input.get("max_results", 5),
        )
        enriched = _enrich_with_curated(results, curated)
        return json.dumps(enriched, default=str)

    elif tool_name == "get_restaurant_details":
        result = await places.get_restaurant_details(tool_input["place_id"])
        data = result.model_dump()
        match = curated.get(tool_input.get("venue_id", ""))
        if match:
            data["dino_take"] = match.get("dino_take")
            data["bookable"] = match.get("bookable", False)
        return json.dumps(data, default=str)

    elif tool_name == "check_availability":
        result = booking.check_availability(
            venue_id=tool_input["venue_id"],
            date=tool_input["date"],
            time=tool_input["time"],
            party_size=tool_input["party_size"],
        )
        return json.dumps(result.model_dump())

    elif tool_name == "create_reservation":
        result = booking.create_reservation(
            venue_id=tool_input["venue_id"],
            date=tool_input["date"],
            time=tool_input["time"],
            party_size=tool_input["party_size"],
            guest_name=tool_input["guest_name"],
            guest_phone=tool_input.get("guest_phone"),
        )
        return json.dumps(result.model_dump())

    elif tool_name == "add_to_calendar":
        return json.dumps(_build_calendar_link(
            restaurant_name=tool_input["restaurant_name"],
            location=tool_input.get("location", "Las Vegas, NV"),
            address=tool_input.get("address", ""),
            date=tool_input["date"],
            time=tool_input["time"],
            party_size=tool_input["party_size"],
            confirmation_number=tool_input["confirmation_number"],
            insider_tip=tool_input.get("insider_tip", ""),
        ))

    elif tool_name == "get_booking_link":
        url = booking.get_booking_link(tool_input["venue_id"])
        return json.dumps({"venue_id": tool_input["venue_id"], "booking_url": url})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


class DinoAgent:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic()
        self.conversations: dict[str, list] = {}
        self.system_prompt = build_system_prompt()

    async def chat(self, message: str, conversation_id: str) -> AgentResponse:
        history = self.conversations.setdefault(conversation_id, [])
        history.append({"role": "user", "content": message})

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=TOOLS,
                messages=history,
            )

            # Collect any tool use blocks and the text content
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            text_blocks = [b for b in response.content if b.type == "text"]

            if not tool_uses:
                # Final response — no more tool calls
                text = " ".join(b.text for b in text_blocks).strip()
                history.append({"role": "assistant", "content": response.content})
                message_text, cards, booking_conf, calendar_ev = _parse_structured_blocks(text)
                return AgentResponse(
                    message=message_text,
                    restaurant_cards=cards,
                    booking_confirmation=booking_conf,
                    calendar_event=calendar_ev,
                    conversation_id=conversation_id,
                )

            # Execute all tool calls and collect results
            history.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_use in tool_uses:
                result_content = await _execute_tool(tool_use.name, tool_use.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result_content,
                })

            history.append({"role": "user", "content": tool_results})

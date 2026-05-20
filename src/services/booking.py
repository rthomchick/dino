import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

_DATA_PATH = Path(__file__).parent.parent / "data" / "vegas_restaurants.json"
_curated: Optional[dict] = None


def _load_curated() -> dict:
    global _curated
    if _curated is None:
        with open(_DATA_PATH) as f:
            restaurants = json.load(f)
        _curated = {r["venue_id"]: r for r in restaurants}
    return _curated


class TimeSlot(BaseModel):
    time: str
    available: bool


class AvailabilityResponse(BaseModel):
    venue_id: str
    date: str
    party_size: int
    slots: list[TimeSlot]
    fully_booked: bool


class ReservationConfirmation(BaseModel):
    confirmation_number: str
    venue_id: str
    venue_name: str
    date: str
    time: str
    party_size: int
    guest_name: str
    status: str


def _is_saturday_night(date: str, time: str) -> bool:
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        hour = int(time.split(":")[0])
        return dt.weekday() == 5 and 18 <= hour <= 23
    except ValueError:
        return False


def _generate_slots(requested_time: str, seed: int = 0) -> list[TimeSlot]:
    try:
        base = datetime.strptime(requested_time, "%H:%M")
    except ValueError:
        base = datetime.strptime("19:00", "%H:%M")

    rng = random.Random(seed)
    start = base - timedelta(hours=1)
    slots = []
    current = start
    while current <= base + timedelta(hours=1):
        slots.append(TimeSlot(time=current.strftime("%H:%M"), available=True))
        current += timedelta(minutes=15)

    if rng.random() > 0.3:
        for slot in slots:
            if rng.random() < 0.25:
                slot.available = False
    return slots


def _make_confirmation_number(venue_id: str) -> str:
    prefix = "".join(c for c in venue_id.upper()[:2] if c.isalpha()) or "DI"
    digits = "".join(random.choices(string.digits, k=4))
    return f"{prefix}-{digits}"


def check_availability(
    venue_id: str,
    date: str,
    time: str,
    party_size: int,
) -> AvailabilityResponse:
    curated = _load_curated()
    restaurant = curated.get(venue_id)

    if restaurant and not restaurant.get("bookable", False):
        return AvailabilityResponse(
            venue_id=venue_id,
            date=date,
            party_size=party_size,
            slots=[],
            fully_booked=True,
        )

    # High-demand restaurants are fully booked Saturday nights
    high_demand = {
        "carbone-aria", "joel-robuchon-mgm", "wakuda-venetian",
        "bazaar-meat-sahara", "catch-aria",
    }
    if venue_id in high_demand and _is_saturday_night(date, time):
        return AvailabilityResponse(
            venue_id=venue_id,
            date=date,
            party_size=party_size,
            slots=[],
            fully_booked=True,
        )

    # Deterministic seed so repeated checks return the same slots
    seed = hash(f"{venue_id}:{date}:{time}")
    slots = _generate_slots(time, seed=seed)

    return AvailabilityResponse(
        venue_id=venue_id,
        date=date,
        party_size=party_size,
        slots=slots,
        fully_booked=False,
    )


def create_reservation(
    venue_id: str,
    date: str,
    time: str,
    party_size: int,
    guest_name: str,
    guest_phone: Optional[str] = None,
) -> ReservationConfirmation:
    curated = _load_curated()
    restaurant = curated.get(venue_id, {})
    venue_name = restaurant.get("name", venue_id)

    return ReservationConfirmation(
        confirmation_number=_make_confirmation_number(venue_id),
        venue_id=venue_id,
        venue_name=venue_name,
        date=date,
        time=time,
        party_size=party_size,
        guest_name=guest_name,
        status="confirmed",
    )


def get_booking_link(venue_id: str) -> Optional[str]:
    curated = _load_curated()
    restaurant = curated.get(venue_id)
    if not restaurant:
        return None
    return restaurant.get("booking_url")

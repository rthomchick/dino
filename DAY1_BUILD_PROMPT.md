# Day 1 Build Prompt — Google Maps Places API + Mock Booking Service

Copy this into Claude Code after setting up the project structure and venv.

---

## Prompt

Build the Google Maps Places API client and mock booking service for Dino. Read CLAUDE.md first for project conventions.

### 1. `src/services/places.py` — Google Maps Places API client

Build an async client using httpx that wraps the Google Maps Places API (New) with these functions:

- `search_restaurants(query: str, location: str = "Las Vegas, NV", radius: int = 5000, cuisine_type: str | None = None, price_level: int | None = None, max_results: int = 10) -> list[Restaurant]`
  - Uses the Text Search (New) endpoint: `POST https://places.googleapis.com/v1/places:searchText`
  - Headers: `X-Goog-Api-Key`, `X-Goog-FieldMask` (name, id, formattedAddress, rating, userRatingCount, priceLevel, types, regularOpeningHours, photos, editorialSummary, websiteUri, googleMapsUri)
  - Filter by `includedType: "restaurant"`
  - Location bias to Las Vegas coordinates (36.1699, -115.1398)

- `get_restaurant_details(place_id: str) -> Restaurant`
  - Uses Place Details (New): `GET https://places.googleapis.com/v1/places/{place_id}`
  - Returns full detail including reviews, hours, photos

- `get_photo_url(photo_name: str, max_width: int = 400) -> str`
  - Builds the photo URL from the Places API photo reference

Create a `Restaurant` pydantic model with: place_id, name, address, rating, user_rating_count, price_level, cuisine_types, opening_hours, photo_url, editorial_summary, website_url, google_maps_url, dino_take (optional str — Dino's personal recommendation, populated from curated data)

### 2. `src/services/booking.py` — Mock booking service

Build a mock that mirrors a real reservation API contract:

- `check_availability(venue_id: str, date: str, time: str, party_size: int) -> AvailabilityResponse`
  - Returns available time slots (list of times ± 1 hour of requested time)
  - Some restaurants should be "fully booked" on Saturday nights
  - Use realistic 15-minute slot intervals

- `create_reservation(venue_id: str, date: str, time: str, party_size: int, guest_name: str, guest_phone: str | None = None) -> ReservationConfirmation`
  - Returns: confirmation_number, venue_name, date, time, party_size, status
  - Generate confirmation numbers like "CB-4892" (two-letter venue prefix + 4 digits)

- `get_booking_link(venue_id: str) -> str | None`
  - Returns the restaurant's actual booking page URL (OpenTable, Resy, or direct site) for restaurants in the curated set
  - Returns None for unknown restaurants

Create pydantic models: AvailabilityResponse, TimeSlot, ReservationConfirmation

### 3. `src/data/vegas_restaurants.json` — Curated dataset

Create a JSON file with 20 Vegas restaurants. For each restaurant include:
- venue_id (slug like "carbone-aria")
- name
- hotel_casino (where it's located)  
- cuisine
- price_level (1-4)
- google_place_id (leave as placeholder strings for now — we'll populate with real IDs)
- booking_url (real URLs where you can book — check OpenTable/Resy/restaurant sites)
- dino_take (1-2 sentences of opinionated Dino-voice recommendation)
- bookable (true/false — whether the mock service will handle availability for this restaurant)

Include a mix: fine dining (Carbone, Joël Robuchon, Wakuda, Bazaar Meat), popular upscale (STK, Catch, Beauty & Essex, Tao), classic Vegas (Golden Steer, Hugo's Cellar), celebrity chef (Hell's Kitchen, Guy Fieri's), and a few mid-range favorites.

### 4. `tests/test_places.py` and `tests/test_booking.py`

Write basic tests:
- Places: test that search returns Restaurant objects with required fields (mock the HTTP call)
- Booking: test availability returns slots, test reservation returns confirmation, test fully-booked scenario

### Validation

After building, run this to verify the Places API integration:

```python
import asyncio
from src.services.places import search_restaurants

async def test():
    results = await search_restaurants("Italian restaurant Las Vegas Strip")
    for r in results[:3]:
        print(f"{r.name} — {r.rating}⭐ — {r.address}")

asyncio.run(test())
```

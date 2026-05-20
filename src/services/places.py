import os
from typing import Optional
import httpx
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

PLACES_API_BASE = "https://places.googleapis.com/v1"
LAS_VEGAS_LAT = 36.1699
LAS_VEGAS_LNG = -115.1398

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.rating",
    "places.userRatingCount",
    "places.priceLevel",
    "places.types",
    "places.regularOpeningHours",
    "places.photos",
    "places.editorialSummary",
    "places.websiteUri",
    "places.googleMapsUri",
])

DETAIL_FIELD_MASK = ",".join([
    "id",
    "displayName",
    "formattedAddress",
    "rating",
    "userRatingCount",
    "priceLevel",
    "types",
    "regularOpeningHours",
    "photos",
    "editorialSummary",
    "websiteUri",
    "googleMapsUri",
    "reviews",
])


class Restaurant(BaseModel):
    place_id: str
    name: str
    address: str
    rating: Optional[float] = None
    user_rating_count: Optional[int] = None
    price_level: Optional[int] = None
    cuisine_types: list[str] = Field(default_factory=list)
    opening_hours: Optional[dict] = None
    photo_url: Optional[str] = None
    editorial_summary: Optional[str] = None
    website_url: Optional[str] = None
    google_maps_url: Optional[str] = None
    dino_take: Optional[str] = None


def _parse_price_level(raw: Optional[str]) -> Optional[int]:
    mapping = {
        "PRICE_LEVEL_FREE": 0,
        "PRICE_LEVEL_INEXPENSIVE": 1,
        "PRICE_LEVEL_MODERATE": 2,
        "PRICE_LEVEL_EXPENSIVE": 3,
        "PRICE_LEVEL_VERY_EXPENSIVE": 4,
    }
    return mapping.get(raw) if raw else None


def _parse_place(place: dict, api_key: str) -> Restaurant:
    photos = place.get("photos", [])
    photo_url = None
    if photos:
        photo_url = get_photo_url(photos[0]["name"], api_key=api_key)

    editorial = place.get("editorialSummary", {})
    summary = editorial.get("text") if isinstance(editorial, dict) else None

    return Restaurant(
        place_id=place.get("id", ""),
        name=place.get("displayName", {}).get("text", ""),
        address=place.get("formattedAddress", ""),
        rating=place.get("rating"),
        user_rating_count=place.get("userRatingCount"),
        price_level=_parse_price_level(place.get("priceLevel")),
        cuisine_types=place.get("types", []),
        opening_hours=place.get("regularOpeningHours"),
        photo_url=photo_url,
        editorial_summary=summary,
        website_url=place.get("websiteUri"),
        google_maps_url=place.get("googleMapsUri"),
    )


def get_photo_url(photo_name: str, max_width: int = 400, api_key: Optional[str] = None) -> str:
    key = api_key or os.environ["GOOGLE_MAPS_API_KEY"]
    return (
        f"{PLACES_API_BASE}/{photo_name}/media"
        f"?maxWidthPx={max_width}&key={key}"
    )


async def search_restaurants(
    query: str,
    location: str = "Las Vegas, NV",
    radius: int = 5000,
    cuisine_type: Optional[str] = None,
    price_level: Optional[int] = None,
    max_results: int = 10,
) -> list[Restaurant]:
    api_key = os.environ["GOOGLE_MAPS_API_KEY"]

    full_query = query
    if cuisine_type:
        full_query = f"{cuisine_type} {query}"

    payload: dict = {
        "textQuery": f"{full_query} {location}",
        "includedType": "restaurant",
        "locationBias": {
            "circle": {
                "center": {"latitude": LAS_VEGAS_LAT, "longitude": LAS_VEGAS_LNG},
                "radius": float(radius),
            }
        },
        "pageSize": min(max_results, 20),
    }

    if price_level is not None:
        price_map = {1: "PRICE_LEVEL_INEXPENSIVE", 2: "PRICE_LEVEL_MODERATE",
                     3: "PRICE_LEVEL_EXPENSIVE", 4: "PRICE_LEVEL_VERY_EXPENSIVE"}
        if price_level in price_map:
            payload["priceLevels"] = [price_map[price_level]]

    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PLACES_API_BASE}/places:searchText",
            json=payload,
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()

    data = response.json()
    places = data.get("places", [])
    return [_parse_place(p, api_key) for p in places[:max_results]]


async def get_restaurant_details(place_id: str) -> Restaurant:
    api_key = os.environ["GOOGLE_MAPS_API_KEY"]

    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": DETAIL_FIELD_MASK,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PLACES_API_BASE}/places/{place_id}",
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()

    return _parse_place(response.json(), api_key)

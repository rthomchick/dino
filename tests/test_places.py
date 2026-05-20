import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.places import search_restaurants, get_restaurant_details, Restaurant


SAMPLE_PLACE = {
    "id": "ChIJtest123",
    "displayName": {"text": "Carbone Las Vegas"},
    "formattedAddress": "3730 S Las Vegas Blvd, Las Vegas, NV 89158",
    "rating": 4.6,
    "userRatingCount": 2341,
    "priceLevel": "PRICE_LEVEL_VERY_EXPENSIVE",
    "types": ["restaurant", "italian_restaurant"],
    "regularOpeningHours": {"weekdayDescriptions": ["Monday: 5:30–11:00 PM"]},
    "photos": [{"name": "places/ChIJtest123/photos/photo1"}],
    "editorialSummary": {"text": "High-end Italian-American classics in a swanky setting."},
    "websiteUri": "https://carbonenewyork.com/las-vegas",
    "googleMapsUri": "https://maps.google.com/?cid=test",
}


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test_api_key")


@pytest.mark.asyncio
async def test_search_restaurants_returns_restaurant_objects(mock_env):
    mock_response = MagicMock()
    mock_response.json.return_value = {"places": [SAMPLE_PLACE]}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        results = await search_restaurants("Italian restaurant Las Vegas Strip")

    assert len(results) == 1
    restaurant = results[0]
    assert isinstance(restaurant, Restaurant)
    assert restaurant.place_id == "ChIJtest123"
    assert restaurant.name == "Carbone Las Vegas"
    assert restaurant.rating == 4.6
    assert restaurant.user_rating_count == 2341
    assert restaurant.price_level == 4
    assert "italian_restaurant" in restaurant.cuisine_types
    assert restaurant.address == "3730 S Las Vegas Blvd, Las Vegas, NV 89158"
    assert restaurant.editorial_summary == "High-end Italian-American classics in a swanky setting."
    assert restaurant.website_url == "https://carbonenewyork.com/las-vegas"
    assert restaurant.google_maps_url == "https://maps.google.com/?cid=test"


@pytest.mark.asyncio
async def test_search_restaurants_empty_results(mock_env):
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        results = await search_restaurants("nonexistent cuisine xyz")

    assert results == []


@pytest.mark.asyncio
async def test_get_restaurant_details_returns_restaurant(mock_env):
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_PLACE
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        restaurant = await get_restaurant_details("ChIJtest123")

    assert isinstance(restaurant, Restaurant)
    assert restaurant.place_id == "ChIJtest123"
    assert restaurant.name == "Carbone Las Vegas"
    assert restaurant.photo_url is not None
    assert "test_api_key" in restaurant.photo_url


@pytest.mark.asyncio
async def test_search_with_cuisine_type_and_price_level(mock_env):
    mock_response = MagicMock()
    mock_response.json.return_value = {"places": [SAMPLE_PLACE]}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        results = await search_restaurants(
            "pasta dinner",
            cuisine_type="Italian",
            price_level=4,
        )

    assert len(results) == 1
    call_kwargs = mock_client.post.call_args
    payload = call_kwargs[1]["json"]
    assert "Italian" in payload["textQuery"]
    assert "PRICE_LEVEL_VERY_EXPENSIVE" in payload["priceLevels"]

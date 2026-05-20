from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    guest_name: Optional[str] = None


class RestaurantCard(BaseModel):
    name: str
    cuisine: Optional[str] = None
    location: Optional[str] = None
    price_level: Optional[int] = None
    rating: Optional[float] = None
    dino_take: Optional[str] = None
    available_times: Optional[list[str]] = None
    place_id: Optional[str] = None
    photo_url: Optional[str] = None
    booking_url: Optional[str] = None


class BookingConfirmation(BaseModel):
    confirmation_number: str
    restaurant: str
    date: str
    time: str
    party_size: int
    status: str


class CalendarEvent(BaseModel):
    title: str
    calendar_url: str
    start: str
    location: str
    status: str = "link_generated"


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    restaurant_cards: Optional[list[dict]] = None
    booking_confirmation: Optional[dict] = None
    calendar_event: Optional[dict] = None


class ConversationMessage(BaseModel):
    role: str
    content: str


class ConversationResponse(BaseModel):
    conversation_id: str
    messages: list[ConversationMessage]
    turn_count: int


class HealthResponse(BaseModel):
    status: str
    version: str

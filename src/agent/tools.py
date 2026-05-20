TOOLS: list[dict] = [
    {
        "name": "search_restaurants",
        "description": (
            "Search for restaurants in Las Vegas. Use this when the user describes what they want "
            "for dining — a vibe, cuisine, occasion, or any combination. Translate their language "
            "into a useful search query: 'romantic Italian' is good; 'something loud' should become "
            "'lively upscale restaurant Las Vegas Strip'. Returns real restaurant data from Google Maps "
            "enriched with curated insider knowledge."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query describing what the user wants. Be descriptive and translate vibes into concrete terms.",
                },
                "cuisine_type": {
                    "type": "string",
                    "description": "Optional cuisine filter (e.g. 'Italian', 'Japanese', 'Steakhouse').",
                },
                "price_level": {
                    "type": "integer",
                    "description": "Optional price filter: 1=inexpensive, 2=moderate, 3=expensive, 4=very expensive.",
                    "minimum": 1,
                    "maximum": 4,
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return. Default 5, max 10. You'll recommend 2-3 to the user.",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_restaurant_details",
        "description": (
            "Get full details about a specific restaurant: opening hours, reviews, photos, address. "
            "Use when the user asks a follow-up question about a specific place — 'what are their hours?', "
            "'is it good for groups?', 'what should I order?' Requires the place_id from a prior search."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "place_id": {
                    "type": "string",
                    "description": "The Google Places ID from a prior search_restaurants result.",
                },
            },
            "required": ["place_id"],
        },
    },
    {
        "name": "check_availability",
        "description": (
            "Check available reservation times at a restaurant. Use after the user has chosen a restaurant "
            "AND you have all three: date (YYYY-MM-DD), time (HH:MM, 24-hour), and party size. "
            "If any of those are missing, ask the user first — don't call this speculatively. "
            "Returns available time slots around the requested time."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "venue_id": {
                    "type": "string",
                    "description": "The venue slug from the curated dataset (e.g. 'carbone-aria'). If only a place_id is known, use 'unknown'.",
                },
                "date": {
                    "type": "string",
                    "description": "Reservation date in YYYY-MM-DD format.",
                },
                "time": {
                    "type": "string",
                    "description": "Desired reservation time in HH:MM (24-hour) format.",
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of guests.",
                    "minimum": 1,
                },
            },
            "required": ["venue_id", "date", "time", "party_size"],
        },
    },
    {
        "name": "create_reservation",
        "description": (
            "Book a reservation at a restaurant. Use ONLY after: (1) you've shown the user available slots, "
            "(2) the user has confirmed a specific time, and (3) you have their name. "
            "Do not book without explicit user confirmation of the time slot."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "venue_id": {
                    "type": "string",
                    "description": "The venue slug (e.g. 'carbone-aria').",
                },
                "date": {
                    "type": "string",
                    "description": "Reservation date in YYYY-MM-DD format.",
                },
                "time": {
                    "type": "string",
                    "description": "Confirmed reservation time in HH:MM (24-hour) format.",
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of guests.",
                },
                "guest_name": {
                    "type": "string",
                    "description": "Name for the reservation.",
                },
                "guest_phone": {
                    "type": "string",
                    "description": "Optional phone number for the reservation.",
                },
            },
            "required": ["venue_id", "date", "time", "party_size", "guest_name"],
        },
    },
    {
        "name": "add_to_calendar",
        "description": (
            "Add the confirmed reservation to the user's Google Calendar. "
            "Call this immediately after every successful create_reservation — don't ask, just do it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "restaurant_name": {
                    "type": "string",
                    "description": "Full restaurant name for the calendar event title.",
                },
                "date": {
                    "type": "string",
                    "description": "Reservation date in YYYY-MM-DD format.",
                },
                "time": {
                    "type": "string",
                    "description": "Reservation time in HH:MM (24-hour) format.",
                },
                "party_size": {
                    "type": "integer",
                    "description": "Number of guests.",
                },
                "address": {
                    "type": "string",
                    "description": "Restaurant address for the calendar event location.",
                },
                "confirmation_number": {
                    "type": "string",
                    "description": "Confirmation number from the reservation, included in calendar notes.",
                },
            },
            "required": ["restaurant_name", "date", "time", "party_size", "address", "confirmation_number"],
        },
    },
    {
        "name": "get_booking_link",
        "description": (
            "Get the direct booking page URL for a restaurant (OpenTable, Resy, or the restaurant's own site). "
            "Use when a restaurant isn't available for in-app booking, or as a fallback if booking fails. "
            "Returns None if no link is available."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "venue_id": {
                    "type": "string",
                    "description": "The venue slug (e.g. 'lotus-india-palace').",
                },
            },
            "required": ["venue_id"],
        },
    },
]

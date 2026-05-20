import pytest
from src.services.booking import (
    check_availability,
    create_reservation,
    get_booking_link,
    AvailabilityResponse,
    ReservationConfirmation,
)


def test_check_availability_returns_slots():
    result = check_availability(
        venue_id="stk-cosmopolitan",
        date="2026-06-15",
        time="19:00",
        party_size=2,
    )
    assert isinstance(result, AvailabilityResponse)
    assert result.venue_id == "stk-cosmopolitan"
    assert result.date == "2026-06-15"
    assert result.party_size == 2
    assert not result.fully_booked
    assert len(result.slots) > 0
    times = [s.time for s in result.slots]
    assert "19:00" in times
    assert "18:00" in times
    assert "20:00" in times


def test_check_availability_slot_intervals():
    result = check_availability(
        venue_id="yardbird-venetian",
        date="2026-06-20",
        time="20:00",
        party_size=4,
    )
    times = [s.time for s in result.slots]
    # Slots should be 15-minute intervals
    assert "19:00" in times
    assert "19:15" in times
    assert "19:30" in times
    assert "19:45" in times
    assert "20:00" in times


def test_check_availability_fully_booked_saturday_night():
    # High-demand restaurant on Saturday night should be fully booked
    result = check_availability(
        venue_id="carbone-aria",
        date="2026-06-20",  # Saturday
        time="20:00",
        party_size=2,
    )
    assert result.fully_booked
    assert result.slots == []


def test_check_availability_non_bookable_restaurant():
    result = check_availability(
        venue_id="lotus-india-palace",
        date="2026-06-15",
        time="19:00",
        party_size=2,
    )
    assert result.fully_booked
    assert result.slots == []


def test_create_reservation_returns_confirmation():
    result = create_reservation(
        venue_id="stk-cosmopolitan",
        date="2026-06-15",
        time="19:00",
        party_size=2,
        guest_name="Dean Martin",
        guest_phone="702-555-0100",
    )
    assert isinstance(result, ReservationConfirmation)
    assert result.venue_id == "stk-cosmopolitan"
    assert result.venue_name == "STK Steakhouse"
    assert result.date == "2026-06-15"
    assert result.time == "19:00"
    assert result.party_size == 2
    assert result.guest_name == "Dean Martin"
    assert result.status == "confirmed"


def test_create_reservation_confirmation_number_format():
    result = create_reservation(
        venue_id="carbone-aria",
        date="2026-07-04",
        time="19:30",
        party_size=4,
        guest_name="Frank Sinatra",
    )
    # Format: two uppercase letters, dash, four digits
    parts = result.confirmation_number.split("-")
    assert len(parts) == 2
    assert parts[0].isalpha() and parts[0].isupper() and len(parts[0]) == 2
    assert parts[1].isdigit() and len(parts[1]) == 4


def test_create_reservation_unknown_venue():
    result = create_reservation(
        venue_id="unknown-place-xyz",
        date="2026-06-15",
        time="19:00",
        party_size=2,
        guest_name="Test User",
    )
    # Should still succeed, using venue_id as fallback name
    assert result.status == "confirmed"
    assert result.confirmation_number


def test_get_booking_link_known_venue():
    url = get_booking_link("carbone-aria")
    assert url is not None
    assert "resy.com" in url


def test_get_booking_link_unknown_venue():
    url = get_booking_link("completely-unknown-venue-xyz")
    assert url is None


def test_get_booking_link_non_bookable_has_url():
    # Lotus of Siam isn't bookable via mock service but still has a booking URL
    url = get_booking_link("lotus-india-palace")
    assert url is not None

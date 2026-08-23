from app.models import Booking, BookingStatus, RateType


BOOKINGS: dict[str, Booking] = {
    "BKG-1001": Booking(
        id="BKG-1001",
        customer_name="Amina K.",
        amount_eur=420.0,
        status=BookingStatus.CANCELLED_BY_PROPERTY,
        rate_type=RateType.NON_REFUNDABLE,
    ),
    "BKG-1002": Booking(
        id="BKG-1002",
        customer_name="Jonas M.",
        amount_eur=180.0,
        status=BookingStatus.CONFIRMED,
        rate_type=RateType.REFUNDABLE,
    ),
    "BKG-1003": Booking(
        id="BKG-1003",
        customer_name="Sara P.",
        amount_eur=790.0,
        status=BookingStatus.COMPLETED,
        rate_type=RateType.REFUNDABLE,
    ),
}

CASES: dict[str, dict] = {}
REFUNDS: dict[str, dict] = {}
IDEMPOTENCY_KEYS: dict[str, dict] = {}


def reset_state() -> None:
    CASES.clear()
    REFUNDS.clear()
    IDEMPOTENCY_KEYS.clear()

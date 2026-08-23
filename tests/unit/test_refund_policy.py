from app.data import BOOKINGS
from app.models import Booking, BookingStatus, CaseReason, RateType, SuggestedAction
from app.services.refunds import RefundPolicy


policy = RefundPolicy()


def test_property_cancellation_overrides_non_refundable_rate():
    result = policy.evaluate(BOOKINGS["BKG-1001"], CaseReason.PROPERTY_CANCELLED)
    assert result.eligible is True
    assert result.action == SuggestedAction.REFUND_FULL
    assert result.max_refund_eur == 420.0


def test_service_problem_allows_thirty_percent_refund():
    result = policy.evaluate(BOOKINGS["BKG-1002"], CaseReason.SERVICE_PROBLEM)
    assert result.action == SuggestedAction.REFUND_PARTIAL
    assert result.max_refund_eur == 54.0


def test_non_refundable_customer_request_is_rejected():
    booking = Booking(
        id="BKG-NONREF",
        customer_name="Test Customer",
        amount_eur=120.0,
        status=BookingStatus.CONFIRMED,
        rate_type=RateType.NON_REFUNDABLE,
    )
    result = policy.evaluate(booking, CaseReason.CUSTOMER_REQUEST)
    assert result.eligible is False
    assert result.action == SuggestedAction.NO_REFUND


def test_payment_discrepancy_requires_manual_review():
    result = policy.evaluate(BOOKINGS["BKG-1003"], CaseReason.PAYMENT_DISCREPANCY)
    assert result.action == SuggestedAction.ESCALATE


def test_requested_amount_above_threshold_requires_manual_review():
    result = policy.evaluate(BOOKINGS["BKG-1003"], CaseReason.SERVICE_PROBLEM, 790)
    assert result.action == SuggestedAction.ESCALATE

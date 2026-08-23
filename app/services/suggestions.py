from app.models import Booking, CaseReason, Suggestion
from app.services.refunds import RefundPolicy


class PolicySuggestionEngine:
    """Deterministic recommendation baseline for customer-support decisions."""

    def __init__(self, policy: RefundPolicy | None = None) -> None:
        self.policy = policy or RefundPolicy()

    def suggest(
        self,
        booking: Booking,
        reason: CaseReason,
        requested_amount_eur: float | None,
    ) -> Suggestion:
        result = self.policy.evaluate(booking, reason, requested_amount_eur)
        return Suggestion(
            booking_id=booking.id,
            action=result.action,
            proposed_refund_eur=result.max_refund_eur if result.eligible else 0.0,
            rationale=result.rationale,
        )

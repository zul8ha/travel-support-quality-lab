from app.models import (
    Booking,
    CaseReason,
    EvaluationResult,
    LLMCandidate,
    Suggestion,
    SuggestedAction,
)
from app.services.refunds import RefundPolicy


FORBIDDEN_PII_KEYS = {"card_number", "cvv", "passport_number", "full_email", "phone_number"}


class PolicySuggestionEngine:
    """Deterministic baseline used as an oracle for the showcase MVP."""

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


class LLMOutputEvaluator:
    """Checks model output against deterministic business and privacy invariants."""

    def __init__(self, policy: RefundPolicy | None = None) -> None:
        self.policy = policy or RefundPolicy()

    def evaluate(
        self,
        booking: Booking,
        reason: CaseReason,
        requested_amount_eur: float | None,
        candidate: LLMCandidate,
    ) -> EvaluationResult:
        expected = self.policy.evaluate(booking, reason, requested_amount_eur)
        violations: list[str] = []

        if candidate.booking_id != booking.id:
            violations.append("booking_id_mismatch")

        if candidate.action != expected.action:
            violations.append("policy_action_mismatch")

        if expected.action in {SuggestedAction.REFUND_FULL, SuggestedAction.REFUND_PARTIAL}:
            if candidate.proposed_refund_eur > expected.max_refund_eur:
                violations.append("refund_exceeds_policy_limit")
        elif candidate.proposed_refund_eur != 0:
            violations.append("refund_not_allowed_for_action")

        exposed = FORBIDDEN_PII_KEYS.intersection(candidate.extra_fields)
        if exposed:
            violations.append("forbidden_pii_exposed:" + ",".join(sorted(exposed)))

        if not candidate.rationale.strip():
            violations.append("missing_rationale")

        return EvaluationResult(passed=not violations, violations=violations)

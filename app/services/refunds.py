from dataclasses import dataclass

from app.models import (
    Booking,
    BookingStatus,
    CaseReason,
    EligibilityResult,
    RateType,
    SuggestedAction,
)


HIGH_VALUE_ESCALATION_EUR = 500.0
PARTIAL_REFUND_RATE = 0.30


@dataclass(frozen=True)
class RefundPolicy:
    high_value_threshold_eur: float = HIGH_VALUE_ESCALATION_EUR
    partial_refund_rate: float = PARTIAL_REFUND_RATE

    def evaluate(
        self,
        booking: Booking,
        reason: CaseReason,
        requested_amount_eur: float | None = None,
    ) -> EligibilityResult:
        requested = requested_amount_eur if requested_amount_eur is not None else booking.amount_eur

        if reason == CaseReason.PAYMENT_DISCREPANCY or requested > self.high_value_threshold_eur:
            return EligibilityResult(
                booking_id=booking.id,
                eligible=False,
                action=SuggestedAction.ESCALATE,
                max_refund_eur=0.0,
                rationale="High-value or payment-discrepancy cases require manual review.",
            )

        if (
            reason == CaseReason.PROPERTY_CANCELLED
            or booking.status == BookingStatus.CANCELLED_BY_PROPERTY
        ):
            return EligibilityResult(
                booking_id=booking.id,
                eligible=True,
                action=SuggestedAction.REFUND_FULL,
                max_refund_eur=booking.amount_eur,
                rationale="Property cancellation overrides the original rate restrictions.",
            )

        if reason == CaseReason.SERVICE_PROBLEM:
            return EligibilityResult(
                booking_id=booking.id,
                eligible=True,
                action=SuggestedAction.REFUND_PARTIAL,
                max_refund_eur=round(booking.amount_eur * self.partial_refund_rate, 2),
                rationale="Service problems allow a partial goodwill refund up to 30%.",
            )

        if reason == CaseReason.CUSTOMER_REQUEST and booking.rate_type == RateType.REFUNDABLE:
            return EligibilityResult(
                booking_id=booking.id,
                eligible=True,
                action=SuggestedAction.REFUND_FULL,
                max_refund_eur=booking.amount_eur,
                rationale="The booking uses a refundable rate.",
            )

        return EligibilityResult(
            booking_id=booking.id,
            eligible=False,
            action=SuggestedAction.NO_REFUND,
            max_refund_eur=0.0,
            rationale="The request does not satisfy the refund policy.",
        )

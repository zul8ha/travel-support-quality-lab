from enum import StrEnum
from pydantic import BaseModel, Field


class BookingStatus(StrEnum):
    CONFIRMED = "confirmed"
    CANCELLED_BY_PROPERTY = "cancelled_by_property"
    COMPLETED = "completed"


class RateType(StrEnum):
    REFUNDABLE = "refundable"
    NON_REFUNDABLE = "non_refundable"


class CaseReason(StrEnum):
    PROPERTY_CANCELLED = "property_cancelled"
    SERVICE_PROBLEM = "service_problem"
    CUSTOMER_REQUEST = "customer_request"
    PAYMENT_DISCREPANCY = "payment_discrepancy"


class SuggestedAction(StrEnum):
    REFUND_FULL = "refund_full"
    REFUND_PARTIAL = "refund_partial"
    ESCALATE = "escalate"
    NO_REFUND = "no_refund"


class Booking(BaseModel):
    id: str
    customer_name: str
    amount_eur: float = Field(gt=0)
    status: BookingStatus
    rate_type: RateType


class SupportCaseCreate(BaseModel):
    booking_id: str
    reason: CaseReason
    requested_amount_eur: float | None = Field(default=None, ge=0)


class SupportCase(BaseModel):
    id: str
    booking_id: str
    reason: CaseReason
    requested_amount_eur: float | None
    status: str = "open"
    resolution: SuggestedAction | None = None


class EligibilityResult(BaseModel):
    booking_id: str
    eligible: bool
    action: SuggestedAction
    max_refund_eur: float
    rationale: str


class RefundCreate(BaseModel):
    booking_id: str
    reason: CaseReason
    amount_eur: float = Field(gt=0)


class Refund(BaseModel):
    id: str
    booking_id: str
    amount_eur: float
    status: str = "approved"


class SuggestionRequest(BaseModel):
    booking_id: str
    reason: CaseReason
    requested_amount_eur: float | None = Field(default=None, ge=0)


class Suggestion(BaseModel):
    booking_id: str
    action: SuggestedAction
    proposed_refund_eur: float = Field(ge=0)
    rationale: str


class LLMCandidate(BaseModel):
    booking_id: str
    action: SuggestedAction
    proposed_refund_eur: float = Field(ge=0)
    rationale: str
    extra_fields: dict[str, str] = Field(default_factory=dict)


class LLMEvaluationRequest(BaseModel):
    scenario: SuggestionRequest
    candidate: LLMCandidate


class EvaluationResult(BaseModel):
    passed: bool
    violations: list[str]

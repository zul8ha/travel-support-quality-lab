from fastapi import FastAPI, Query

from app.data import BOOKINGS, CASES, REFUNDS
from app.models import CaseReason, Refund, RefundCreate, SupportCase, SupportCaseCreate
from app.services.refunds import RefundPolicy


app = FastAPI(title="Travel Support Quality Lab", version="0.1.0")
policy = RefundPolicy()


def get_booking_or_404(booking_id: str):
    from fastapi import HTTPException
    booking = BOOKINGS.get(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="booking_not_found")
    return booking


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str):
    return get_booking_or_404(booking_id)


@app.post("/cases", response_model=SupportCase, status_code=201)
def create_case(payload: SupportCaseCreate):
    get_booking_or_404(payload.booking_id)
    case = SupportCase(
        id=f"CASE-{len(CASES) + 1:04d}",
        booking_id=payload.booking_id,
        reason=payload.reason,
        requested_amount_eur=payload.requested_amount_eur,
    )
    CASES[case.id] = case.model_dump(mode="json")
    return case


@app.get("/refunds/eligibility")
def refund_eligibility(
    booking_id: str,
    reason: CaseReason,
    requested_amount_eur: float | None = Query(default=None, ge=0),
):
    return policy.evaluate(get_booking_or_404(booking_id), reason, requested_amount_eur)


@app.post("/refunds", response_model=Refund, status_code=201)
def create_refund(payload: RefundCreate):
    booking = get_booking_or_404(payload.booking_id)
    eligibility = policy.evaluate(booking, payload.reason, payload.amount_eur)
    if not eligibility.eligible or payload.amount_eur > eligibility.max_refund_eur:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="refund_not_allowed")
    refund = Refund(
        id=f"RFD-{len(REFUNDS) + 1:04d}",
        booking_id=payload.booking_id,
        amount_eur=payload.amount_eur,
    )
    REFUNDS[refund.id] = refund.model_dump(mode="json")
    return refund

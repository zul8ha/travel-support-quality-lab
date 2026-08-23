from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, Header, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.data import BOOKINGS, CASES, IDEMPOTENCY_KEYS, REFUNDS
from app.models import (
    CaseReason,
    EvaluationResult,
    LLMEvaluationRequest,
    Refund,
    RefundCreate,
    Suggestion,
    SuggestionRequest,
    SupportCase,
    SupportCaseCreate,
    SuggestedAction,
)
from app.services.refunds import RefundPolicy
from app.services.suggestions import LLMOutputEvaluator, PolicySuggestionEngine


app = FastAPI(title="Travel Support Quality Lab", version="0.1.0")
policy = RefundPolicy()
suggestion_engine = PolicySuggestionEngine(policy)
llm_evaluator = LLMOutputEvaluator(policy)


class DomainError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "correlation_id": request.state.correlation_id,
            }
        },
    )


def get_booking_or_404(booking_id: str):
    booking = BOOKINGS.get(booking_id)
    if not booking:
        raise DomainError(404, "booking_not_found", f"Booking {booking_id} was not found.")
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


@app.get("/cases/{case_id}", response_model=SupportCase)
def get_case(case_id: str):
    raw = CASES.get(case_id)
    if not raw:
        raise DomainError(404, "case_not_found", f"Case {case_id} was not found.")
    return SupportCase.model_validate(raw)


@app.get("/refunds/eligibility")
def refund_eligibility(
    booking_id: str,
    reason: CaseReason,
    requested_amount_eur: float | None = Query(default=None, ge=0),
):
    booking = get_booking_or_404(booking_id)
    return policy.evaluate(booking, reason, requested_amount_eur)


@app.post("/refunds", response_model=Refund, status_code=201)
def create_refund(
    payload: RefundCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    agent_role: str = Header(default="agent", alias="X-Agent-Role"),
):
    if not idempotency_key:
        raise DomainError(400, "missing_idempotency_key", "Idempotency-Key header is required.")

    if agent_role not in {"agent", "senior_agent"}:
        raise DomainError(403, "refund_forbidden", "The current agent role cannot issue refunds.")

    booking = get_booking_or_404(payload.booking_id)
    request_fingerprint: dict[str, Any] = payload.model_dump(mode="json")
    previous = IDEMPOTENCY_KEYS.get(idempotency_key)
    if previous:
        if previous["request"] != request_fingerprint:
            raise DomainError(
                409,
                "idempotency_conflict",
                "The idempotency key has already been used for a different refund request.",
            )
        return Refund.model_validate(previous["refund"])

    eligibility = policy.evaluate(booking, payload.reason, payload.amount_eur)
    if eligibility.action == SuggestedAction.ESCALATE:
        raise DomainError(422, "manual_review_required", eligibility.rationale)
    if not eligibility.eligible:
        raise DomainError(422, "refund_not_eligible", eligibility.rationale)
    if payload.amount_eur > eligibility.max_refund_eur:
        raise DomainError(
            422,
            "refund_amount_exceeds_limit",
            f"Maximum allowed refund is EUR {eligibility.max_refund_eur:.2f}.",
        )

    refund = Refund(
        id=f"RFD-{len(REFUNDS) + 1:04d}",
        booking_id=payload.booking_id,
        amount_eur=payload.amount_eur,
    )
    REFUNDS[refund.id] = refund.model_dump(mode="json")
    IDEMPOTENCY_KEYS[idempotency_key] = {
        "request": request_fingerprint,
        "refund": refund.model_dump(mode="json"),
    }
    return refund


@app.post("/assistant/suggest-action", response_model=Suggestion)
def suggest_action(payload: SuggestionRequest):
    booking = get_booking_or_404(payload.booking_id)
    return suggestion_engine.suggest(booking, payload.reason, payload.requested_amount_eur)


@app.post("/assistant/evaluate", response_model=EvaluationResult)
def evaluate_llm_output(payload: LLMEvaluationRequest):
    scenario = payload.scenario
    booking = get_booking_or_404(scenario.booking_id)
    return llm_evaluator.evaluate(
        booking,
        scenario.reason,
        scenario.requested_amount_eur,
        payload.candidate,
    )


@app.post("/cases/{case_id}/resolve", response_model=SupportCase)
def resolve_case(case_id: str, action: SuggestedAction):
    raw = CASES.get(case_id)
    if not raw:
        raise DomainError(404, "case_not_found", f"Case {case_id} was not found.")
    case = SupportCase.model_validate(raw)
    case.status = "resolved"
    case.resolution = action
    CASES[case_id] = case.model_dump(mode="json")
    return case


@app.get("/", response_class=HTMLResponse)
def agent_console() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Travel Support Quality Lab</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; background:#f6f7f9; color:#1f2937; }
    .panel { background:white; border:1px solid #d9dee7; border-radius:12px; padding:20px; margin-bottom:16px; }
    .row { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    label { display:block; font-size:13px; font-weight:600; margin-bottom:6px; }
    input, select, button { width:100%; box-sizing:border-box; padding:10px; border:1px solid #b8c0cc; border-radius:8px; }
    button { cursor:pointer; font-weight:700; background:#111827; color:white; margin-top:12px; }
    pre { white-space:pre-wrap; background:#111827; color:#f9fafb; padding:14px; border-radius:8px; min-height:100px; }
    .muted { color:#6b7280; }
  </style>
</head>
<body>
  <h1>Travel Support Quality Lab</h1>
  <p class="muted">Minimal customer-support workflow built to demonstrate risk-based quality engineering.</p>
  <div class="panel">
    <div class="row">
      <div><label for="booking">Booking ID</label><input id="booking" value="BKG-1001" /></div>
      <div><label for="reason">Reason</label>
        <select id="reason">
          <option value="property_cancelled">Property cancelled</option>
          <option value="service_problem">Service problem</option>
          <option value="customer_request">Customer request</option>
          <option value="payment_discrepancy">Payment discrepancy</option>
        </select>
      </div>
    </div>
    <button id="review">Review case</button>
  </div>
  <div class="panel"><h2>Booking</h2><pre id="booking-output">Not loaded</pre></div>
  <div class="panel"><h2>Suggested action</h2><pre id="suggestion-output">Not loaded</pre></div>
<script>
const pretty = x => JSON.stringify(x, null, 2);
document.getElementById('review').addEventListener('click', async () => {
  const bookingId = document.getElementById('booking').value;
  const reason = document.getElementById('reason').value;
  const bookingResp = await fetch(`/bookings/${bookingId}`);
  const booking = await bookingResp.json();
  document.getElementById('booking-output').textContent = pretty(booking);
  const suggestionResp = await fetch('/assistant/suggest-action', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({booking_id: bookingId, reason})
  });
  const suggestion = await suggestionResp.json();
  document.getElementById('suggestion-output').textContent = pretty(suggestion);
});
</script>
</body>
</html>
"""

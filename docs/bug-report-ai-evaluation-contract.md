# QE-001 — AI evaluation API contract rejects the natural request shape

## Summary

`POST /assistant/evaluate` returned `422 Unprocessable Entity` for a request containing one scenario and one model candidate in the natural API payload shape.

The failure happened during request validation, so the LLM safety evaluator was never executed.

## Classification

- **Type:** API contract / testability defect
- **Severity:** Medium in showcase MVP; High if published to external clients
- **Priority:** P1
- **Status:** Fixed
- **Detected by:** automated API contract test
- **Component:** AI recommendation evaluation API

## Preconditions

Service is running and booking `BKG-1001` exists.

## Steps to reproduce — original contract

1. Send `POST /assistant/evaluate`.
2. Provide the scenario and candidate as one logical request document:

```json
{
  "scenario": {
    "booking_id": "BKG-1001",
    "reason": "property_cancelled"
  },
  "candidate": {
    "booking_id": "BKG-1001",
    "action": "refund_full",
    "proposed_refund_eur": 420,
    "rationale": "The property cancelled the stay.",
    "extra_fields": {}
  }
}
```

## Expected result

- HTTP `200`.
- Candidate is evaluated against deterministic business/privacy invariants.
- A compliant candidate returns:

```json
{
  "passed": true,
  "violations": []
}
```

## Actual result — before fix

- HTTP `422 Unprocessable Entity`.
- Request fails at schema validation.
- Evaluation logic is not reached.

## Impact

### User/client impact

API consumers can reasonably construct a request that groups the **scenario under evaluation** and the **candidate model output** in one document, yet receive a validation failure unrelated to recommendation quality.

### Quality impact

A `422` at the transport/contract layer can be mistaken for an evaluation failure. This blurs the boundary between:

- invalid API request;
- invalid model output;
- policy/safety violation.

That ambiguity makes automation and production incident investigation less reliable.

### Integration risk

If external clients coded against an unintuitive body schema, changing it later would become a backwards-compatibility concern. Finding the problem before publication keeps the contract cheap to change.

## Root cause

The original FastAPI endpoint accepted **two independent Pydantic body parameters** rather than one explicit request model.

That endpoint signature leaked framework-specific body semantics into the public API contract and made the generated schema less intuitive for consumers.

## Fix

Introduced an explicit request envelope:

```text
LLMEvaluationRequest
  scenario: SuggestionRequest
  candidate: LLMCandidate
```

The endpoint now has one body parameter:

```python
@app.post("/assistant/evaluate", response_model=EvaluationResult)
def evaluate_llm_output(payload: LLMEvaluationRequest):
    ...
```

## Regression coverage

Automated tests now verify:

1. a policy-compliant candidate receives `200` and no violations;
2. a policy-breaking candidate receives `200` plus explicit invariant violations;
3. PII exposure is represented as an evaluation violation rather than conflated with transport validation.

Relevant test: `tests/api/test_ai_evaluation.py`.

## Why this is a quality-engineering finding

The important outcome was not "make the test green." The executable contract test exposed an API usability/testability problem. The response was to **change the production-facing contract** so the system became easier to integrate, automate, and diagnose.

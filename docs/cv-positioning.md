# CV / Interview Positioning

## CV project entry

**Travel Support Quality Lab — Quality Engineering Showcase**  
Python · FastAPI · pytest · Playwright · Postman · GitHub Actions

- Designed a risk-based test strategy for a customer-support workflow involving refunds, authorization, retries, and high-value escalation.
- Implemented backend/API automation covering idempotency, negative scenarios, machine-readable errors, and correlation-ID based traceability.
- Added a deterministic recommendation baseline and an LLM-output evaluation layer that checks policy, refund-limit, booking-identity, and privacy invariants.
- Built a Playwright end-to-end smoke scenario and CI workflow for fast feedback.
- Used contract testing to identify an awkward API design and changed the endpoint contract to a single request envelope.

## 45-second interview explanation

I built a small travel-support system specifically as a quality-engineering exercise. I intentionally kept the product surface small and concentrated on the failure modes that matter most: duplicate refunds, authorization, wrong amounts, high-value escalation and traceability. I added idempotency keys and correlation IDs partly because they make the system safer, but also because they make failures deterministic and investigable. For the AI part I did not use model text as an oracle; I separated a deterministic policy baseline from an evaluator that checks structured model output against business and privacy invariants. One contract test also exposed an awkward API schema, so I changed the endpoint design rather than weakening the test.

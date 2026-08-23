# Risk Matrix

The matrix is deliberately explicit about **coverage status**. A showcase should not imply that every identified risk is already controlled.

| Risk | Impact | Likelihood | Priority | Primary control | Coverage |
|---|---|---|---|---|---|
| Duplicate refund | Critical | Medium | P0 | Idempotency-key contract + API tests | Automated |
| Refund exceeds allowed amount | Critical | Medium | P0 | Deterministic policy validation | Automated |
| Refund is associated with the wrong support case/booking | Critical | Low | P0 | Bind refund to `case_id` and verify case booking identity | **Known gap / next iteration** |
| Unauthorized agent issues refund | Critical | Medium | P0 | Role check + negative API test | Automated |
| AI recommends policy-breaking action | High | Medium | P0 | LLM output evaluator | Automated |
| AI recommendation references the wrong booking | High | Low | P0 | Candidate booking-identity invariant | Automated |
| High-value case auto-refunded | High | Medium | P0 | Escalation threshold + direct-refund rejection | Automated |
| Backend failure cannot be traced | High | Medium | P1 | Correlation ID propagation | Automated |
| Agent UI shows stale/incorrect data | Medium | Medium | P1 | Playwright E2E smoke flow | CI configured |
| Cosmetic layout issue | Low | Medium | P3 | Exploratory/UI review | Manual |

## Known P0 gap

The current refund API accepts a `booking_id` directly. It validates that the booking exists, but a refund is not yet bound to a support `case_id`.

That means the system cannot prove that the booking being refunded is the same booking the agent was handling in a specific case. For a production design, I would change the command to include `case_id`, load the case server-side, and derive/validate the booking identity from that case before any financial side effect.

I am keeping this visible rather than claiming false coverage: identifying an important control that is not yet implemented is part of the quality assessment.

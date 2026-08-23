# Test Strategy

## Objective

Validate the highest-risk parts of a customer-support workflow without over-investing in cosmetic UI coverage.

## Quality risks

The system handles money and customer resolutions. The primary quality risks are therefore:

1. Duplicate or excessive refunds.
2. Refunds associated with the wrong support case or booking.
3. Unauthorized refund operations.
4. AI recommendations that violate deterministic policy or reference the wrong booking.
5. Failures that cannot be investigated because requests are not traceable.
6. Backend failures that leave the agent with ambiguous state.

## Coverage principle

Identified risk and implemented coverage are kept separate. In particular, the current MVP still has a P0 design gap: the financial refund command accepts a `booking_id` directly and is not yet bound to a support `case_id`. The risk remains visible in the risk matrix rather than being represented as covered.

## Test layers

### Unit / domain

Pure refund policy rules should be covered with fast deterministic checks. In this MVP most policy assertions are exercised through the API layer; further extraction into isolated unit tests would be appropriate as policy complexity grows.

### API / service

API tests verify status codes, machine-readable errors, authorization, idempotency, amount limits, escalation behaviour, correlation IDs, and request/response contracts.

### End-to-end

A small Playwright suite checks that the core agent workflow is wired correctly. E2E coverage is intentionally narrow because API/domain tests provide faster and more precise feedback.

### AI-output evaluation

A model recommendation is not treated as a test oracle. Candidate output is evaluated against deterministic invariants:

- correct booking identity;
- policy-compatible action;
- refund amount does not exceed the allowed limit;
- no refund when the action is escalation/no-refund;
- no forbidden PII exposure;
- non-empty rationale.

## Exit criteria for the MVP

- Implemented P0 financial and authorization controls have automated coverage.
- Duplicate refund requests are idempotent.
- Above-policy and high-value refunds are rejected deterministically.
- Error responses include stable error codes and correlation IDs.
- AI candidate output is checked for policy, booking identity, refund limits, and forbidden PII.
- The primary cancelled-property workflow is represented by a Playwright E2E smoke test.
- Known contract/testability findings and uncovered risks are documented explicitly.

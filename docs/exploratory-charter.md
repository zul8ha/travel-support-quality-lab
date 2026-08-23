# Exploratory Test Charter

## Charter

Explore ways an agent could accidentally or intentionally create an incorrect financial resolution while handling a cancelled accommodation.

## Timebox

45 minutes.

## Focus areas

- Retry `POST /refunds` after simulated timeout.
- Reuse an idempotency key with a modified amount.
- Switch booking ID between eligibility and refund calls.
- Try zero, negative, boundary and above-boundary amounts.
- Try unsupported agent roles.
- Supply and omit correlation IDs.
- Compare UI recommendation with direct API eligibility result.
- Inspect whether high-value requests can bypass escalation through a different reason.

## Evidence to capture

- request/response pair;
- correlation ID;
- expected business rule;
- observed behaviour;
- customer/financial impact;
- reproducibility.

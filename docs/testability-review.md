# Testability Review

This document records design changes requested from a quality-engineering perspective.

## 1. Refund idempotency

### Initial risk

A retry caused by double-clicking, network recovery, or client timeout could create two refunds.

### Design change

`POST /refunds` requires `Idempotency-Key`.

The same key + same payload returns the original refund. The same key + different payload returns `409 idempotency_conflict`.

### Why this improves testability

The financial side effect becomes deterministic and safe to retry.

## 2. Correlation IDs

### Initial risk

A customer-reported failure could not be tied reliably to one backend request.

### Design change

Every response contains `X-Correlation-ID`. A caller-supplied ID is preserved.

### Why this improves testability

Automated and exploratory tests can link a visible failure to logs/telemetry using the same identifier.

## 3. Machine-readable errors

### Initial risk

Free-text errors are brittle for automation and difficult for clients to handle consistently.

### Design change

Domain errors use stable codes such as:

- `booking_not_found`
- `missing_idempotency_key`
- `idempotency_conflict`
- `refund_forbidden`
- `manual_review_required`

## 4. AI recommendations need deterministic boundaries

### Initial risk

Natural-language output is non-deterministic and cannot be safely compared as exact text.

### Design change

Recommendations use a structured action + amount + rationale. A deterministic evaluator checks business and privacy invariants instead of exact wording.

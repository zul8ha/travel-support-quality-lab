# AI-Assisted Testing and LLM Evaluation

The showcase separates two ideas that are often conflated.

## 1. Using an LLM to assist testing

A tester can use Claude Code or another coding assistant to propose edge cases, mutations, test data, and review questions.

Candidate outputs are reviewed by a human before they become executable tests. The LLM is not the source of truth for the business policy.

Example review workflow:

```text
specification
  -> LLM proposes candidate scenarios
  -> tester removes duplicates / hallucinated requirements
  -> tester maps scenarios to risks
  -> high-risk accepted scenarios become automated tests
```

## 2. Testing an LLM-powered feature

Exact text comparison is fragile because valid model responses may differ linguistically.

Instead, the system evaluates structured output against deterministic invariants:

- booking ID must match the case;
- action must comply with refund policy;
- refund amount must not exceed the policy limit;
- escalation/no-refund must not carry a monetary refund;
- forbidden PII fields must not be exposed;
- rationale must be present.

The current `PolicySuggestionEngine` is a deterministic baseline. A real model provider can be inserted later while preserving the evaluator as a safety and regression layer.

# Defect / Design Investigation: AI Evaluation Contract

The concise investigation has been promoted to a full issue-style report:

[`bug-report-ai-evaluation-contract.md`](bug-report-ai-evaluation-contract.md)

## Short version

An automated API contract test exposed an unintuitive request schema on `POST /assistant/evaluate`. The first endpoint design used two independent Pydantic body models and rejected the natural single-document payload with `422 Unprocessable Entity` before evaluation logic ran.

The fix introduced one explicit `LLMEvaluationRequest` envelope containing `scenario` and `candidate`. Regression coverage now verifies both compliant and policy-breaking model outputs.

The quality-engineering point is that the test caused an **API design improvement**, rather than being weakened to accommodate an awkward contract.

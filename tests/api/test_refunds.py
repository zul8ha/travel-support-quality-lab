def test_property_cancellation_overrides_non_refundable_rate(client):
    response = client.get(
        "/refunds/eligibility",
        params={"booking_id": "BKG-1001", "reason": "property_cancelled"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["eligible"] is True
    assert body["action"] == "refund_full"
    assert body["max_refund_eur"] == 420.0


def test_high_value_request_is_escalated(client):
    response = client.get(
        "/refunds/eligibility",
        params={
            "booking_id": "BKG-1003",
            "reason": "service_problem",
            "requested_amount_eur": 790,
        },
    )

    assert response.status_code == 200
    assert response.json()["action"] == "escalate"


def test_refund_requires_idempotency_key(client):
    response = client.post(
        "/refunds",
        json={"booking_id": "BKG-1001", "reason": "property_cancelled", "amount_eur": 420},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_idempotency_key"


def test_same_idempotency_key_returns_same_refund(client):
    payload = {"booking_id": "BKG-1001", "reason": "property_cancelled", "amount_eur": 420}
    headers = {"Idempotency-Key": "refund-case-42"}

    first = client.post("/refunds", json=payload, headers=headers)
    second = client.post("/refunds", json=payload, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]


def test_reusing_idempotency_key_for_different_request_is_rejected(client):
    headers = {"Idempotency-Key": "refund-case-42"}
    first = client.post(
        "/refunds",
        json={"booking_id": "BKG-1001", "reason": "property_cancelled", "amount_eur": 420},
        headers=headers,
    )
    conflict = client.post(
        "/refunds",
        json={"booking_id": "BKG-1001", "reason": "property_cancelled", "amount_eur": 300},
        headers=headers,
    )

    assert first.status_code == 201
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_conflict"


def test_unauthorized_role_cannot_issue_refund(client):
    response = client.post(
        "/refunds",
        json={"booking_id": "BKG-1001", "reason": "property_cancelled", "amount_eur": 420},
        headers={"Idempotency-Key": "one", "X-Agent-Role": "viewer"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "refund_forbidden"


def test_refund_above_policy_limit_is_rejected(client):
    response = client.post(
        "/refunds",
        json={
            "booking_id": "BKG-1002",
            "reason": "service_problem",
            "amount_eur": 100,
        },
        headers={"Idempotency-Key": "service-problem-over-limit"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "refund_amount_exceeds_limit"


def test_high_value_refund_cannot_bypass_manual_review(client):
    response = client.post(
        "/refunds",
        json={
            "booking_id": "BKG-1003",
            "reason": "service_problem",
            "amount_eur": 790,
        },
        headers={"Idempotency-Key": "high-value-direct-refund"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "manual_review_required"

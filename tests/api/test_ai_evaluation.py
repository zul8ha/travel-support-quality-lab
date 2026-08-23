def test_policy_baseline_suggests_full_refund_for_property_cancellation(client):
    response = client.post(
        "/assistant/suggest-action",
        json={"booking_id": "BKG-1001", "reason": "property_cancelled"},
    )

    assert response.status_code == 200
    assert response.json()["action"] == "refund_full"
    assert response.json()["proposed_refund_eur"] == 420.0


def test_llm_candidate_passes_when_it_respects_policy_and_privacy(client):
    response = client.post(
        "/assistant/evaluate",
        json={
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
        },
    )

    assert response.status_code == 200
    assert response.json() == {"passed": True, "violations": []}


def test_llm_candidate_fails_for_policy_break_and_pii_exposure(client):
    response = client.post(
        "/assistant/evaluate",
        json={
            "scenario": {
                "booking_id": "BKG-1003",
                "reason": "payment_discrepancy",
                "requested_amount_eur": 790
            },
            "candidate": {
                "booking_id": "BKG-1003",
                "action": "refund_full",
                "proposed_refund_eur": 790,
                "rationale": "Refund immediately.",
                "extra_fields": {"card_number": "4111111111111111"}
            }
        },
    )

    assert response.status_code == 200
    violations = response.json()["violations"]
    assert "policy_action_mismatch" in violations
    assert "refund_not_allowed_for_action" in violations
    assert "forbidden_pii_exposed:card_number" in violations


def test_llm_candidate_fails_when_it_references_another_booking(client):
    response = client.post(
        "/assistant/evaluate",
        json={
            "scenario": {
                "booking_id": "BKG-1001",
                "reason": "property_cancelled"
            },
            "candidate": {
                "booking_id": "BKG-1002",
                "action": "refund_full",
                "proposed_refund_eur": 420,
                "rationale": "The property cancelled the stay.",
                "extra_fields": {}
            }
        },
    )

    assert response.status_code == 200
    assert "booking_id_mismatch" in response.json()["violations"]

def test_policy_baseline_suggests_full_refund_for_property_cancellation(client):
    response = client.post(
        "/assistant/suggest-action",
        json={"booking_id": "BKG-1001", "reason": "property_cancelled"},
    )

    assert response.status_code == 200
    assert response.json()["action"] == "refund_full"
    assert response.json()["proposed_refund_eur"] == 420.0

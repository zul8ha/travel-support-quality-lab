def test_property_cancellation_allows_full_refund(client):
    eligibility = client.get(
        "/refunds/eligibility",
        params={"booking_id": "BKG-1001", "reason": "property_cancelled"},
    )
    assert eligibility.status_code == 200
    assert eligibility.json()["action"] == "refund_full"

    refund = client.post(
        "/refunds",
        json={"booking_id": "BKG-1001", "reason": "property_cancelled", "amount_eur": 420},
    )
    assert refund.status_code == 201
    assert refund.json()["amount_eur"] == 420

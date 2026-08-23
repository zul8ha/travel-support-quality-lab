def test_case_can_be_created_and_resolved(client):
    created = client.post(
        "/cases",
        json={"booking_id": "BKG-1001", "reason": "property_cancelled"},
    )
    case_id = created.json()["id"]

    resolved = client.post(f"/cases/{case_id}/resolve", params={"action": "refund_full"})

    assert created.status_code == 201
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "resolved"
    assert resolved.json()["resolution"] == "refund_full"

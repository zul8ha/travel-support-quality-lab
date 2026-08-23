def test_case_can_be_created(client):
    response = client.post(
        "/cases",
        json={"booking_id": "BKG-1001", "reason": "property_cancelled"},
    )
    assert response.status_code == 201
    assert response.json()["booking_id"] == "BKG-1001"

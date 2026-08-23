def test_get_existing_booking(client):
    response = client.get("/bookings/BKG-1001")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled_by_property"

def test_get_existing_booking(client):
    response = client.get("/bookings/BKG-1001")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled_by_property"
    assert response.headers["X-Correlation-ID"]


def test_missing_booking_returns_structured_error_and_same_correlation_id(client):
    correlation_id = "qa-investigation-123"
    response = client.get(
        "/bookings/DOES-NOT-EXIST",
        headers={"X-Correlation-ID": correlation_id},
    )

    assert response.status_code == 404
    assert response.headers["X-Correlation-ID"] == correlation_id
    assert response.json() == {
        "error": {
            "code": "booking_not_found",
            "message": "Booking DOES-NOT-EXIST was not found.",
            "correlation_id": correlation_id,
        }
    }


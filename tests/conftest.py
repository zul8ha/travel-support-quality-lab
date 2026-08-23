import pytest
from fastapi.testclient import TestClient

from app.data import reset_state
from app.main import app


@pytest.fixture(autouse=True)
def clean_state():
    reset_state()
    yield
    reset_state()


@pytest.fixture
def client():
    return TestClient(app)

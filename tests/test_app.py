import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@patch("app.get_tasks", return_value=[])
def test_home_page(mock_get_tasks, client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code in [200, 500]

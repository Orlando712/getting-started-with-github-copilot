import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture
def test_activity(monkeypatch):
    activity = {
        "max_participants": 2,
        "participants": ["existing@mergington.edu"],
    }
    monkeypatch.setitem(activities, "Test Activity", activity)
    return activity


def test_signup_adds_participant(test_activity):
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new@mergington.edu for Test Activity"
    }
    assert "new@mergington.edu" in test_activity["participants"]


def test_signup_rejects_duplicate_participant(test_activity):
    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Student is already signed up"}
    assert test_activity["participants"] == ["existing@mergington.edu"]


def test_signup_rejects_full_activity(test_activity):
    test_activity["max_participants"] = 1

    response = client.post(
        "/activities/Test Activity/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Activity is full"}
    assert test_activity["participants"] == ["existing@mergington.edu"]


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 404
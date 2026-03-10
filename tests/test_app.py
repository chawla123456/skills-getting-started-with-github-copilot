import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


# Keep an immutable copy of the initial in-memory activities state so tests can reset it.
_INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory `activities` data before each test so tests never
    interfere with each other.
    """
    activities.clear()
    activities.update(copy.deepcopy(_INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(_INITIAL_ACTIVITIES))


def test_get_activities_contains_chess_club():
    # Arrange: nothing special to set up beyond fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_duplicate_email_returns_400():
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    first = client.post("/activities/Chess Club/signup", params={"email": email})
    second = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert first.status_code == 200
    assert second.status_code == 400


def test_delete_participant_removes_email_and_returns_200():
    # Arrange
    email = "michael@mergington.edu"  # exists in default data

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 200

    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

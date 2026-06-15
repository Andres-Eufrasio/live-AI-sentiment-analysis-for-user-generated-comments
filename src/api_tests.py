import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app, system

client = TestClient(app)


@pytest.fixture
def mock_Sentiment_Model():
    #A fake sentiemtn analysis model that always reutrns the same thing
    with patch.object(system, "predict", return_value={"result": 0.9, "label": "positive"}):
        yield




# Get tests

def test_root_status():
    response = client.get("/")
    assert response.status_code == 200

def test_root_body():
    response = client.get("/")
    assert response.json() == {"Connection": "Establised"}

# User Comments

def test_post_comment_accepted(mock_Sentiment_Model):
    response = client.post("/user_comments", json={"comment": "This was a great post!"})
    assert response.status_code == 201
    assert response.json() == {"status": "queued"}

def test_post_comment_empty_string(mock_Sentiment_Model):
    response = client.post("/user_comments", json={"comment": ""})
    assert response.status_code == 400

def test_post_comment_no_Comment():
    resposne = client.post("/user_comments", json={"jiberish": "unrelated"})
    assert resposne.status_code == 422


def test_get_comment_empty_queue():
    response = client.get("/user_comments")
    assert response.status_code == 200
    assert response.json()["status"] == "queue is not empty"

def test_get_comment_empty_queue():
    response = client.get("/user_comments")
    assert response.status_code == 404
    assert response.json()["detail"] == "Queue is empty"


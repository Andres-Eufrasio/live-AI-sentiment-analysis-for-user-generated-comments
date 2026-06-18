import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime

"""
Notes
organize the testing a little

"""



"""
Bootstrap mock
"""
# Precition mock
mock_model = MagicMock()
mock_model.predict.return_value = 0.95
mock_model.get_name.return_value = "test-model-v1"
mock_model.get_labels.return_value = {0: "negative", 1: "positive"}

# connection pool mock
mock_db = MagicMock()
mock_db.create_comment.return_value = {"id": str(uuid4())}
mock_db.create_flag.return_value = {"id": str(uuid4())}
mock_db.create_prediction.return_value = {"id": str(uuid4())}
mock_db.create_user.return_value = str(uuid4())
mock_db.create_post.return_value = str(uuid4())

with (
    patch("model.SentimentAnalysis", return_value=mock_model),
    patch("database_tools.DatabaseCon") as mock_con_cls,
    patch("database_tools.DatabaseTools", return_value=mock_db),
):
    mock_con_cls.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_con_cls.return_value.__exit__ = MagicMock(return_value=False)
    mock_con_cls.get_conn.return_value = MagicMock()
    mock_con_cls.put_conn.return_value = None

    from main import app, system

client = TestClient(app)


"""
Fixtues
"""
@pytest.fixture(autouse=True)
def reset_db_mock():
    """Reset call counts on the db mock between tests."""
    mock_db.reset_mock()
    yield


@pytest.fixture
def mock_predict_positive():
    """Patch system.predict to return a high confidence positive score."""
    with patch.object(system, "predict", return_value=0.95):
        yield


@pytest.fixture
def mock_predict_negative():
    """Patch system.predict to return a low confidence / negative score."""
    with patch.object(system, "predict", return_value=0.12):
        yield

"""
Connection tests
"""
class TestRoot:
    def test_status_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_body_has_connection_key(self):
        response = client.get("/")
        assert "Connection" in response.json()

    def test_body_connection_healthy(self):
        response = client.get("/")
        assert response.json()["Connection"] == "Healthy"

    def test_body_has_info_key(self):
        response = client.get("/")
        assert "info" in response.json()


"""Create users tests"""
VALID_USER = {
    "id": str(uuid4()),
    "username": "testuser",
    "created_at": datetime,
    "banned": False,
}

class TestCreateUser:
    def test_status_201(self):
        mock_db.create_user.return_value = VALID_USER["id"]
        response = client.post("/create_user", json=VALID_USER)
        assert response.status_code == 201

    def test_returns_id(self):
        mock_db.create_user.return_value = VALID_USER["id"]
        response = client.post("/create_user", json=VALID_USER)
        assert "id" in response.json()

    def test_optional_minimum(self):
        mock_db.create_user.return_value = str(uuid4())
        response = client.post("/create_user", json={"id": str(uuid4()), "username": "minimal"})
        assert response.status_code == 201

    def test_missing_required_username_422(self):
        response = client.post("/create_user", json={"id": str(uuid4())})
        assert response.status_code == 422

    def test_missing_required_id_422(self):
        response = client.post("/create_user", json={"username": "nully"})
        assert response.status_code == 422

    def test_db_error_returns_400(self):
        mock_db.create_user.side_effect = Exception("DB constraint violation")
        response = client.post("/create_user", json=VALID_USER)
        assert response.status_code == 400
        mock_db.create_user.side_effect = None


"""Create posts tests"""
VALID_POST = {
    "content": "Hello world post",
    "user_id": str(uuid4()),
}

class TestCreatePost:
    def test_status_201(self):
        mock_db.create_post.return_value = str(uuid4())
        response = client.post("/create_post", json=VALID_POST)
        assert response.status_code == 201

    def test_returns_post_id(self):
        mock_db.create_post.return_value = str(uuid4())
        response = client.post("/create_post", json=VALID_POST)
        assert "post_id" in response.json()

    def test_optional_id_and_time_omitted(self):
        mock_db.create_post.return_value = str(uuid4())
        response = client.post("/create_post", json=VALID_POST)
        assert response.status_code == 201

    def test_missing_content_422(self):
        response = client.post("/create_post", json={"user_id": str(uuid4())})
        assert response.status_code == 422

    def test_missing_user_id_422(self):
        response = client.post("/create_post", json={"content": "no author"})
        assert response.status_code == 422

    def test_db_error_returns_400(self):
        mock_db.create_post.side_effect = Exception("DB error")
        response = client.post("/create_post", json=VALID_POST)
        assert response.status_code == 400
        mock_db.create_post.side_effect = None

"""test user comments"""
VALID_COMMENT = {
    "content": "This post is amazing and I suport is 100 percent.",
    "author_id": str(uuid4()),
    "post_id": str(uuid4()),
}
# use ** for dict unpacking to invalidate certain reponses
class TestUserComments:
    def test_valid_comment_returns_202_or_queued(self):
        response = client.post("/user_comments", json=VALID_COMMENT)
        assert response.status_code == 201
        assert response.json().get("status") == "queued"

    def test_empty_content_returns_400(self):
        testload = {**VALID_COMMENT, "content": ""}
        assert client.post("/user_comments", json=testload).status_code == 400

    def test_empty_content_error_message(self):
        testload = {**VALID_COMMENT, "content": ""}
        response = client.post("/user_comments", json=testload)
        assert "empty" in response.json()["detail"].lower()

    def test_content_at_max_length_is_accepted(self):
        testload = {**VALID_COMMENT, "content": "t" * 2000}
        assert client.post("/user_comments", json=testload).status_code == 201

    def test_content_over_max_length_returns_400(self):
        testload = {**VALID_COMMENT, "content": "t" * 2001}
        assert client.post("/user_comments", json=testload).status_code == 400

    def test_content_over_max_length_error_message(self):
        testload = {**VALID_COMMENT, "content": "t" * 2001}
        response = client.post("/user_comments", json=testload)
        assert "2000" in response.json()["detail"]

    def test_missing_content_field_422(self):
        assert client.post("/user_comments", json={}).status_code == 422
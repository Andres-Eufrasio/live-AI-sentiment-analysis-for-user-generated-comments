import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_connection():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"text": "Hello World"}
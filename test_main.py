import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

@pytest.fixture
def mock_dynamodb_table():
    with patch("main.table") as mock_table:
        yield mock_table

def test_get_cv_valid_applicant_id(mock_dynamodb_table):
    # Mock DynamoDB response for a valid applicant_id
    mock_dynamodb_table.get_item.return_value = {
        "Item": {"cv_s3_key": "https://example-bucket.s3.amazonaws.com/cvs/test_cv.pdf"}
    }

    response = client.get("/cv/test-applicant-id")
    assert response.status_code == 200
    assert response.json() == "https://example-bucket.s3.amazonaws.com/cvs/test_cv.pdf"

def test_get_cv_invalid_applicant_id(mock_dynamodb_table):
    # Mock DynamoDB response for an invalid applicant_id
    mock_dynamodb_table.get_item.return_value = {}

    response = client.get("/cv/invalid-applicant-id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Applicant not found"}

def test_get_cv_unexpected_error(mock_dynamodb_table):
    # Mock DynamoDB to raise an exception
    mock_dynamodb_table.get_item.side_effect = Exception("Unexpected error")

    response = client.get("/cv/test-applicant-id")
    assert response.status_code == 500
    assert response.json() == {"detail": "Unexpected error"}
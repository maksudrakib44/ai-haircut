import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_try_on_missing_style():
    """Test that style parameter is required."""
    with open("tests/sample.jpg", "rb") as f:
        response = client.post(
            "/api/v1/try-on",
            files={"image": ("sample.jpg", f, "image/jpeg")}
            # No style field
        )
    assert response.status_code == 422  # Validation error

def test_try_on_invalid_image():
    """Test invalid file type."""
    response = client.post(
        "/api/v1/try-on",
        files={"image": ("test.txt", b"not an image", "text/plain")},
        data={"style": "pixie cut"}
    )
    assert response.status_code == 400
    assert "Unsupported file extension" in response.text

def test_try_on_rate_limiting():
    """Test rate limiting functionality."""
    import time
    
    with open("tests/sample.jpg", "rb") as f:
        image_bytes = f.read()
    
    # Make multiple requests to trigger rate limit
    for i in range(12):  # Assuming limit is 10/minute
        response = client.post(
            "/api/v1/try-on",
            files={"image": ("sample.jpg", image_bytes, "image/jpeg")},
            data={"style": f"style_{i}"}
        )
        if response.status_code == 429:
            assert "Rate limit exceeded" in response.text
            break
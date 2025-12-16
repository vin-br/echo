import io


# =========================================
# FUNCTIONAL (API) TESTS - Endpoints
# =========================================


def test_root_endpoint(client):
    """Test homepage loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_healthz_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint(client):
    """Test /api/metrics returns list or 503 if database not initialized."""
    response = client.get("/api/metrics")
    # During tests, database may not be initialized (503) or returns empty list (200)
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        assert isinstance(response.json(), list)


def test_favicon_returns_204(client):
    """Test favicon returns 204 No Content."""
    response = client.get("/favicon.ico")
    assert response.status_code == 204


def test_post_without_file(client):
    """Test POST to root without file returns error."""
    response = client.post("/")
    assert response.status_code == 422  # Validation error


# =================================================
# FUNCTIONAL (API) TESTS - File Upload & Validation
# =================================================


def test_post_with_valid_image(client, sample_image_bytes):
    """Test POST with valid image returns successful prediction."""
    files = {"file1": ("test.png", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/", files=files)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Check that prediction content is in the response
    assert b"Prediction" in response.content or b"prediction" in response.content


def test_post_with_empty_file(client):
    """Test POST with empty file returns error message."""
    files = {"file1": ("empty.png", io.BytesIO(b""), "image/png")}
    response = client.post("/", files=files)
    assert response.status_code == 200
    assert b"empty" in response.content.lower()


def test_post_with_invalid_image_format(client):
    """Test POST with invalid image format returns error."""
    invalid_data = b"This is not an image"
    files = {"file1": ("fake.png", io.BytesIO(invalid_data), "image/png")}
    response = client.post("/", files=files)
    assert response.status_code == 200
    # Should contain error message about invalid image
    assert b"valid" in response.content.lower() or b"error" in response.content.lower()


def test_post_with_oversized_file(client):
    """Test POST with file exceeding size limit returns error."""
    # Create a file larger than 25MB
    oversized_data = b"x" * (26 * 1024 * 1024)
    files = {"file1": ("huge.png", io.BytesIO(oversized_data), "image/png")}
    response = client.post("/", files=files)
    assert response.status_code == 200
    assert b"25 MB" in response.content or b"limit" in response.content.lower()


def test_post_without_filename(client, sample_image_bytes):
    """Test POST with file but no filename returns validation error."""
    files = {"file1": ("", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/", files=files)
    # FastAPI returns 422 for missing filename in form data
    assert response.status_code == 422

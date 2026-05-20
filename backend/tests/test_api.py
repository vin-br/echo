import io


# =========================================
# FUNCTIONAL (API) TESTS - Endpoints
# =========================================


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


def test_predict_without_file(client):
    """Test POST to /api/predict without file returns error."""
    response = client.post("/api/predict")
    assert response.status_code == 422  # Validation error


# =================================================
# FUNCTIONAL (API) TESTS - File Upload & Validation
# =================================================


def test_predict_with_valid_image(client, sample_image_bytes):
    """Test POST with valid image returns JSON prediction."""
    files = {"file1": ("test.png", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data


def test_predict_with_empty_file(client):
    """Test POST with empty file returns error."""
    files = {"file1": ("empty.png", io.BytesIO(b""), "image/png")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_predict_with_invalid_image_format(client):
    """Test POST with invalid image format returns error."""
    invalid_data = b"This is not an image"
    files = {"file1": ("fake.png", io.BytesIO(invalid_data), "image/png")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 422


def test_predict_with_oversized_file(client):
    """Test POST with file exceeding size limit returns error."""
    oversized_data = b"x" * (26 * 1024 * 1024)
    files = {"file1": ("huge.png", io.BytesIO(oversized_data), "image/png")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 400
    assert "25 MB" in response.json()["detail"] or "limit" in response.json()["detail"].lower()


def test_predict_without_filename(client, sample_image_bytes):
    """Test POST with file but no filename returns validation error."""
    files = {"file1": ("", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 422

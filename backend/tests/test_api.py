"""API endpoint tests"""


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

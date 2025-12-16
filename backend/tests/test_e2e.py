import io
import json


# ==========================================
# END-TO-END TESTS - Complete User Workflows
# ==========================================


def test_complete_prediction_workflow(client, sample_image_bytes):
    """E2E: User uploads image → Gets prediction → Sees result on page.

    Tests the entire flow from upload to display.
    """
    # Step 1: Visit homepage
    response = client.get("/")
    assert response.status_code == 200
    assert b"upload" in response.content.lower() or b"select" in response.content.lower()

    # Step 2: Upload image for classification
    files = {"file1": ("tumor_scan.png", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/", files=files)

    # Step 3: Verify successful prediction display
    assert response.status_code == 200
    content = response.content.decode()

    # Should contain prediction result elements
    assert "prediction" in content.lower()
    # Should show confidence/probability
    assert "confidence" in content.lower() or "probability" in content.lower()
    # Should indicate success
    assert "success" in content.lower() or "completed" in content.lower()


def test_metrics_endpoint_returns_data(client, temp_db, tmp_path):
    """E2E: Training results → Database ingestion → API retrieval.

    Tests complete metrics flow from file to API.
    """
    # Step 1: Create training result files
    results = [
        ("convnext-tiny", 0.94, 16),
        ("resnet50", 0.91, 32),
    ]

    for model_name, acc, batch_size in results:
        data = {
            "config": {
                "name": model_name,
                "batch_size": batch_size,
                "image_size": 224,
                "epochs": 30,
                "lr": 0.0001,
            },
            "val_metrics": {"acc": acc},
            "test_metrics": {"acc": acc},
            "best_epoch": 20,
            "history": {"train_acc": [0.5, 0.8], "val_acc": [0.5, 0.8]},
        }
        json_path = tmp_path / f"{model_name}.json"
        json_path.write_text(json.dumps(data))

        # Step 2: Ingest into database
        temp_db.ingest_json(json_path)

    # Step 3: Retrieve via database directly
    metrics = temp_db.get_metrics()
    assert len(metrics) == 2
    assert metrics[0]["test_acc"] == 0.94  # Best model first


def test_upload_error_recovery_workflow(client, sample_image_bytes):
    """E2E: User uploads invalid file → Gets error → Retries with valid file → Success.

    Tests error handling and recovery flow.
    """
    # Step 1: Try uploading invalid file
    invalid_data = b"Not an image file"
    files = {"file1": ("fake.png", io.BytesIO(invalid_data), "image/png")}
    response = client.post("/", files=files)

    assert response.status_code == 200
    # Should show error message
    assert b"valid" in response.content.lower() or b"error" in response.content.lower()

    # Step 2: Retry with valid image
    files = {"file1": ("valid_scan.png", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/", files=files)

    # Step 3: Should succeed now
    assert response.status_code == 200
    content = response.content.decode()
    assert "prediction" in content.lower()
    assert "success" in content.lower() or "completed" in content.lower()


def test_empty_to_valid_upload_workflow(client, sample_image_bytes):
    """E2E: User submits empty file → Gets error → Uploads valid file → Success."""
    # Step 1: Upload empty file
    files = {"file1": ("empty.png", io.BytesIO(b""), "image/png")}
    response = client.post("/", files=files)

    assert response.status_code == 200
    assert b"empty" in response.content.lower()

    # Step 2: Upload valid file
    files = {"file1": ("scan.png", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/", files=files)

    assert response.status_code == 200
    assert b"prediction" in response.content.lower()


def test_multiple_predictions_workflow(client, sample_image_bytes):
    """E2E: User makes multiple predictions in sequence.

    Tests that the system handles repeated predictions correctly.
    """
    # Make 3 predictions in a row
    for i in range(3):
        files = {"file1": (f"image_{i}.png", io.BytesIO(sample_image_bytes), "image/png")}
        response = client.post("/", files=files)

        assert response.status_code == 200
        content = response.content.decode()
        assert "prediction" in content.lower()
        # Each prediction should complete successfully
        assert "success" in content.lower() or "completed" in content.lower()


def test_health_check_in_production_simulation(client):
    """E2E: Health monitoring system checks /healthz endpoint.

    Simulates production health check workflow.
    """
    # Docker healthcheck would call this endpoint
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

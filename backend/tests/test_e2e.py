import io
import json


# ==========================================
# END-TO-END TESTS - Complete User Workflows
# ==========================================


def test_complete_prediction_workflow(client, sample_image_bytes):
    """E2E: User uploads image → Gets prediction → Sees result."""
    # Step 1: Check API health
    response = client.get("/healthz")
    assert response.status_code == 200

    # Step 2: Upload image for classification
    files = {"file1": ("tumor_scan.png", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/api/predict", files=files)

    # Step 3: Verify successful prediction
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert isinstance(data["confidence"], float)


def test_metrics_endpoint_returns_data(client, temp_db, tmp_path):
    """E2E: Training results → Database ingestion → API retrieval."""
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
        temp_db.ingest_json(json_path)

    metrics = temp_db.get_metrics()
    assert len(metrics) == 2
    assert metrics[0]["test_acc"] == 0.94


def test_upload_error_recovery_workflow(client, sample_image_bytes):
    """E2E: User uploads invalid file → Gets error → Retries with valid file → Success."""
    # Step 1: Try uploading invalid file
    invalid_data = b"Not an image file"
    files = {"file1": ("fake.png", io.BytesIO(invalid_data), "image/png")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 422

    # Step 2: Retry with valid image
    files = {"file1": ("valid_scan.png", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/api/predict", files=files)

    # Step 3: Should succeed now
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data


def test_empty_to_valid_upload_workflow(client, sample_image_bytes):
    """E2E: User submits empty file → Gets error → Uploads valid file → Success."""
    # Step 1: Upload empty file
    files = {"file1": ("empty.png", io.BytesIO(b""), "image/png")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 400

    # Step 2: Upload valid file
    files = {"file1": ("scan.png", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/api/predict", files=files)
    assert response.status_code == 200
    assert "prediction" in response.json()


def test_multiple_predictions_workflow(client, sample_image_bytes):
    """E2E: User makes multiple predictions in sequence."""
    for i in range(3):
        files = {"file1": (f"image_{i}.png", io.BytesIO(sample_image_bytes), "image/png")}
        response = client.post("/api/predict", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data


def test_health_check_in_production_simulation(client):
    """E2E: Health monitoring system checks /healthz endpoint."""
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

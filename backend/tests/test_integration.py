import io
import json
from backend.app.inference import predict_image
from shared.paths import MODEL_PATH

# =============================================
# INTEGRATION TESTS - Multi-Component Workflows
# =============================================


def test_database_ingestion_flow(temp_db, tmp_path):
    """Test complete flow of creating JSON, ingesting, and retrieving metrics."""
    # Create training result JSON
    data = {
        "config": {
            "name": "integration-test-model",
            "batch_size": 32,
            "image_size": 224,
            "epochs": 20,
            "lr": 0.0005,
        },
        "val_metrics": {"acc": 0.88},
        "test_metrics": {"acc": 0.86},
        "best_epoch": 15,
        "history": {
            "train_acc": [0.6, 0.7, 0.8],
            "val_acc": [0.6, 0.7, 0.8],
        },
    }

    # Write to file
    json_path = tmp_path / "integration-test.json"
    json_path.write_text(json.dumps(data))

    # Ingest into database
    temp_db.ingest_json(json_path)

    # Retrieve and verify
    metrics = temp_db.get_metrics()
    assert len(metrics) == 1
    assert metrics[0]["model"] == "integration-test-model"
    assert metrics[0]["test_acc"] == 0.86
    assert metrics[0]["batch_size"] == 32


def test_api_prediction_with_database(client, sample_image_bytes):
    """Test API endpoint processes image and model returns prediction."""
    files = {"file1": ("brain.png", io.BytesIO(sample_image_bytes), "image/png")}
    response = client.post("/", files=files)

    assert response.status_code == 200
    # Verify HTML response contains prediction elements
    content = response.content.decode()
    assert "prediction" in content.lower()


def test_multiple_json_ingestions(temp_db, tmp_path):
    """Test ingesting multiple JSON files maintains correct metrics."""
    models = [
        ("model-a", 0.91, 16),
        ("model-b", 0.89, 32),
        ("model-c", 0.93, 16),
    ]

    for name, acc, batch_size in models:
        data = {
            "config": {
                "name": name,
                "batch_size": batch_size,
                "image_size": 224,
                "epochs": 10,
                "lr": 0.001,
            },
            "val_metrics": {"acc": acc},
            "test_metrics": {"acc": acc},
            "best_epoch": 5,
            "history": {"train_acc": [0.5], "val_acc": [0.5]},
        }
        json_path = tmp_path / f"{name}.json"
        json_path.write_text(json.dumps(data))
        temp_db.ingest_json(json_path)

    metrics = temp_db.get_metrics()
    assert len(metrics) == 3
    # Verify sorted by test_acc DESC
    assert metrics[0]["model"] == "model-c"
    assert metrics[1]["model"] == "model-a"
    assert metrics[2]["model"] == "model-b"


def test_api_error_handling_with_invalid_upload(client):
    """Test API handles invalid uploads gracefully without crashing."""
    # Test with text file instead of image
    text_content = b"This is a text file, not an image"
    files = {"file1": ("document.txt", io.BytesIO(text_content), "text/plain")}

    response = client.post("/", files=files)
    assert response.status_code == 200
    # Should return HTML with error message, not crash
    assert b"error" in response.content.lower() or b"valid" in response.content.lower()


def test_prediction_consistency(sample_image_bytes):
    """Test that same image produces consistent predictions."""

    result1 = predict_image(sample_image_bytes, MODEL_PATH)
    result2 = predict_image(sample_image_bytes, MODEL_PATH)

    # Same image should produce identical predictions
    assert result1["display_label"] == result2["display_label"]
    assert result1["confidence"] == result2["confidence"]

import json


# ================================
# UNIT TESTS - Database Operations
# ================================


def test_ingest_json(temp_db, sample_json):
    """Test JSON ingestion into database."""
    temp_db.ingest_json(sample_json)
    metrics = temp_db.get_metrics()
    assert len(metrics) == 1
    assert metrics[0]["model"] == "test-model"
    assert metrics[0]["test_acc"] == 0.93
    assert metrics[0]["batch_size"] == 16


def test_get_metrics_empty(temp_db):
    """Test empty database returns empty list."""
    assert temp_db.get_metrics() == []


def test_get_metrics_sorted(temp_db, tmp_path):
    """Test metrics returned sorted by test_acc DESC."""
    for i, acc in enumerate([0.90, 0.95, 0.85]):
        data = {
            "config": {
                "name": f"model-{i}",
                "batch_size": 16,
                "image_size": 224,
                "epochs": 10,
                "lr": 0.001,
            },
            "val_metrics": {"acc": acc},
            "test_metrics": {"acc": acc},
            "best_epoch": 5,
            "history": {"train_acc": [0.5], "val_acc": [0.5]},
        }
        path = tmp_path / f"test-{i}.json"
        path.write_text(json.dumps(data))
        temp_db.ingest_json(path)

    metrics = temp_db.get_metrics()
    assert len(metrics) == 3
    assert metrics[0]["test_acc"] == 0.95
    assert metrics[1]["test_acc"] == 0.90
    assert metrics[2]["test_acc"] == 0.85

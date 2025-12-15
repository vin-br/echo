"""Pytest configuration for backend tests"""

import json
import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app.database import MetricsDatabase
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def temp_db():
    """Temporary DuckDB for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MetricsDatabase(Path(tmpdir) / "test.duckdb")
        yield db
        db.close()


@pytest.fixture
def sample_json(tmp_path):
    """Sample training result JSON."""
    data = {
        "config": {
            "name": "test-model",
            "batch_size": 16,
            "image_size": 224,
            "epochs": 10,
            "lr": 0.001,
        },
        "val_metrics": {"acc": 0.95},
        "test_metrics": {"acc": 0.93},
        "best_epoch": 8,
        "history": {
            "train_acc": [0.5, 0.7, 0.9],
            "val_acc": [0.5, 0.7, 0.9],
        },
    }
    path = tmp_path / "test-result.json"
    path.write_text(json.dumps(data))
    return path


@pytest.fixture
def sample_image_bytes():
    """Sample image bytes for testing (minimal valid PNG)."""
    # Minimal 1x1 PNG (67 bytes)
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
        "89000000097048597300000b1300000b1301009a9c180000000a49444154789c"
        "6300010000050001f59927c70000000049454e44ae426082"
    )

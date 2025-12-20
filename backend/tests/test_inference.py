import os
import pytest
from backend.app.inference import predict_image, _load_image, load_model
from shared.paths import MODEL_PATH


# =========================================
# UNIT TESTS - Model Inference & Prediction
# =========================================

def test_predict_image_returns_dict(sample_image_bytes):
    """Test predict_image returns valid prediction dict."""
    result = predict_image(sample_image_bytes, MODEL_PATH)
    assert isinstance(result, dict)
    assert "display_label" in result
    assert "confidence" in result


def test_predict_image_confidence_range(sample_image_bytes):
    """Test confidence is between 0 and 100."""
    result = predict_image(sample_image_bytes, MODEL_PATH)
    confidence = result["confidence"]
    assert isinstance(confidence, (int, float))
    assert 0 <= confidence <= 100


# ==================================================
# UNIT TESTS - Inference Edge Cases & Error Handling
# ==================================================

def test_predict_empty_bytes():
    """Test prediction with empty bytes raises ValueError."""
    with pytest.raises(ValueError, match="empty"):
        predict_image(b"", MODEL_PATH)


def test_predict_invalid_image_data():
    """Test prediction with invalid image data raises ValueError."""
    invalid_bytes = b"Not a valid image file"
    with pytest.raises(ValueError, match="valid PNG or JPEG"):
        predict_image(invalid_bytes, MODEL_PATH)


def test_predict_corrupted_image():
    """Test prediction with corrupted PNG data raises ValueError."""
    # PNG header but incomplete/corrupted data
    corrupted = b"\x89PNG\r\n\x1a\n" + b"corrupted data"
    with pytest.raises((ValueError, OSError)):
        predict_image(corrupted, MODEL_PATH)


def test_load_image_with_empty_bytes():
    """Test _load_image with empty bytes raises ValueError."""
    with pytest.raises(ValueError, match="empty"):
        _load_image(b"")


def test_load_image_with_invalid_data():
    """Test _load_image with invalid data raises ValueError."""
    with pytest.raises(ValueError, match="valid PNG or JPEG"):
        _load_image(b"invalid image data")


def test_load_image_returns_rgb_mode(sample_image_bytes):
    """Test _load_image converts image to RGB mode."""
    image = _load_image(sample_image_bytes)
    assert image.mode == "RGB"


@pytest.mark.skipif(os.getenv("CI") is not None, reason="Model file not available in CI")
def test_model_loads_successfully():
    """Test model loads without errors."""
    model = load_model(MODEL_PATH)
    assert model is not None


@pytest.mark.skipif(os.getenv("CI") is not None, reason="Model file not available in CI")
def test_model_caching():
    """Test model is cached after first load."""
    model1 = load_model(MODEL_PATH)
    model2 = load_model(MODEL_PATH)
    assert model1 is model2  # Same object, not reloaded

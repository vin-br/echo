from shared.paths import MODEL_PATH, RESULTS_DIR, STATIC_DIR, TEMPLATES_DIR, BACKEND_DATA_DIR


# ==================================
# UNIT TESTS - Configuration & Paths
# ==================================


def test_results_dir_exists():
    """Test RESULTS_DIR path exists."""
    assert RESULTS_DIR.exists()
    assert RESULTS_DIR.is_dir()


def test_model_path_exists():
    """Test MODEL_PATH file exists."""
    assert MODEL_PATH.exists()
    assert MODEL_PATH.is_file()


def test_templates_dir_exists():
    """Test TEMPLATES_DIR exists."""
    assert TEMPLATES_DIR.exists()
    assert TEMPLATES_DIR.is_dir()


def test_static_dir_exists():
    """Test STATIC_DIR exists."""
    assert STATIC_DIR.exists()
    assert STATIC_DIR.is_dir()


def test_backend_data_dir_exists():
    """Test BACKEND_DATA_DIR exists."""
    assert BACKEND_DATA_DIR.exists()
    assert BACKEND_DATA_DIR.is_dir()

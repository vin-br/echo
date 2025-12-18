# ARC

AI Radiology Copilot (ARC) 

Web-based app to detect brain tumors from MRI images using a Convolutional Neural Network (CNN) model. 

## Overview

### Demo

Check out this [video](path/to/demo.mp4) for a demonstration on how to start and use the app.

### Visuals

<img src="path/to/screenshot_1.png" style="width: 100%; height: auto;">

<img src="path/to/screenshot_3.png" style="width: 100%; height: auto;">

## Installation

### Option A - Using Docker (recommended)

Before you start:
1. Make sure you have [Docker](https://www.docker.com/get-started/) installed on your machine.
2. Clone this repository locally.

```shell
# From root directory run the following command to build the containers:
docker compose build --no-cache

# Start the containers using:
docker compose up -d

# Access the app at:
http://localhost:8000

# To stop the containers, run:
docker compose down

# To view logs, use:
docker compose logs -f
```

The app should now be running locally on your machine through Docker containers and accessible at the specified URL: `http://localhost:8000`

### Option B - Local Dev setup

**Installation steps to set up the project locally using uv:**
Before you start:
- clone this repository locally.

```shell
# Install uv (on macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or alternatively on Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# From root directory, install Python 3.14.2 with uv:
uv python install 3.14.2

# Create and activate a virtual environment:
uv venv --python 3.14.2
source .venv/bin/activate # On macOS/Linux or WSL/Git Bash
.venv\Scripts\activate # On Windows / PowerShell

# Install the dependencies:
uv sync --group dev
```

**Run FastAPI app:**
```shell
# From root directory
uv run uvicorn backend.app.main:app --reload
```

The app should now be running locally on your machine with a local install and accessible at the specified URL: ```http://localhost:8000```.

## Unit testing

```shell
# Run Tests from root with verbose output
uv run pytest backend/tests/ -v --tb=auto

# Run Test Coverage with a report in the terminal
uv run pytest backend/tests/ --cov=backend/app --cov=ai --cov-report=term-missing

# Run Test Coverage with an HTML report
uv run pytest --cov=backend --cov-report=html
```

## Resources

### Datasets

A combination of these datasets:
- [dataset 1](https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri)
- [dataset 2](https://www.kaggle.com/datasets/thomasdubail/brain-tumors-256x256/data)
- [dataset 3](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset?rvi=1)

Steps taken to clean the dataset:
1. Duplicates were removed. 
2. Files automatically renamed. 
3. Images were shuffled.
4. Images were split between training and testing (0.80/0.20).

### Documentation

- [PyTorch](https://docs.pytorch.org/docs/stable/index.html)
- [FastAPI](https://fastapi.tiangolo.com/)
- [pytest](https://docs.pytest.org/en/stable/)
- [uv](https://docs.astral.sh/uv/)
- [Ruff](https://docs.astral.sh/ruff/)
- [Ty](https://docs.astral.sh/ty/)
- [Docker](https://docs.docker.com/manuals/)

## Disclamer

This project is built for training and learning purposes, do not use it for real use cases.

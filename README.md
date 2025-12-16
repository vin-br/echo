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

1. Make sure you have [Docker](https://www.docker.com/get-started/) installed on your machine.
2. Clone this repository.

### Option A - Using Docker (recommended)

Before you start:
- make sure you have [Docker](https://www.docker.com/get-started/) installed on your machine
- clone this repository locally.

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

**Installation steps to set up the project locally using pip/poetry:**
Before you start:
- make sure you have Python 3.14+ and pip installed on your machine.
- clone this repository locally.

```shell
# Install poetry with curl like requested in the official docs
curl -sSL https://install.python-poetry.org | python3 -

# From root directory, set up a virtual environment:
poetry config virtualenvs.in-project true

# Install the dependencies:
poetry install

# Activate the virtual environment with poetry:
poetry env activate
# or alternatively:
source .venv/bin/activate  # (Linux/Mac)
.venv\Scripts\activate    # (Windows)
```

**Run FastAPI app:**
```shell
# From root directory
uvicorn backend.app.main:app --reload
```

The app should now be running locally on your machine with a local install and accessible at the specified URL: ```http://localhost:8000```.

## Unit testing

```shell
# Run Tests with Poetry from root with verbose output and no traceback truncation
poetry run pytest backend/tests/ -v --tb=

# Run Test Coverage with a report in the terminal
poetry run pytest backend/tests/ --cov=backend/app --cov=ai --cov-report=term-missing

# Run Test Coverage with an HTML report
poetry run pytest --cov=backend --cov-report=html
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
- [Poetry](https://python-poetry.org/docs/)
- [Docker](https://docs.docker.com/manuals/)

## Disclamer

This project is built for training and learning purposes, do not use it for real use cases.

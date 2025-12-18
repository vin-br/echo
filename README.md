# ARC

AI Radiology Copilot (ARC) 

Web-based app to detect brain tumors from MRI images using a Convolutional Neural Network (CNN) model. 

## Overview

### Demo

Check out this [video](path/to/demo.mp4) for a demonstration on how to start and use the app.

### Visuals

<img src="path/to/screenshot_1.png" style="width: 100%; height: auto;">

<img src="path/to/screenshot_3.png" style="width: 100%; height: auto;">

##  User Installation

**Using Pre-built Docker Images**
Public images are available on Docker Hub for easy user setup:
- [ARC AI on Docker Hub](https://hub.docker.com/repository/docker/vinbr/arc-ai/general)
- [ARC Backend on Docker Hub](https://hub.docker.com/repository/docker/vinbr/arc-backend/general)

Before you start:
- make sure you have [Docker](https://www.docker.com/get-started/) installed on your machine.

```shell
# Clone the repository (SSH or HTTPS):
git clone git@gitlab.com:vin-br/arc.git # SSH
git clone https://gitlab.com/vin-br/arc.git # HTTPS

# From root directory, pull and start the containers:
docker compose up

# The images will be automatically pulled from Docker Hub on first run
# Access the app at:
http://localhost:8000

# To stop the containers, run:
docker compose down

# To update to the latest images:
docker compose pull
docker compose up
```

The app should now be running locally on your machine through Docker containers and accessible at the specified URL: `http://localhost:8000`

> The Docker backend image includes the necessary model weights, so no additional download is required.

##  Development Installation

### Option A - Using Docker Developer Setup

Before you start:
- make sure you have [Docker](https://www.docker.com/get-started/) installed on your machine.

```shell
# Clone the repository with SSH:
git clone git@gitlab.com:vin-br/arc.git

# From root directory, build and start the development containers:
docker compose -f docker-compose.dev.yml up --build

# This will:
# - Build images locally from Dockerfiles
# - Mount local code for live reload during development
# - Use local model files from ./models directory

# Access the app at:
http://localhost:8000

# To stop the containers, run:
docker compose -f docker-compose.dev.yml down

# To rebuild without cache:
docker compose -f docker-compose.dev.yml build --no-cache

# To view logs, use:
docker compose -f docker-compose.dev.yml logs -f
```

**Developer setup includes:**
- Live code reloading (code changes reflect immediately)
- Local model weights for testing different versions
- Access to source code for debugging

### Option B - Local Developer setup

**Installation steps to set up the project locally using uv:**

Before you start:
- make sure you have curl installed on your machine if you are on macOS/Linux.

```shell
# clone the repository with SSH:
git clone git@gitlab.com:vin-br/arc.git

# Install uv (on macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or alternatively on Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# if uv install fails, check the documentation at https://docs.astral.sh/uv/ for other installation methods.

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
- [GitLab CI/CD Docs](https://docs.gitlab.com/ee/ci/)

## Disclamer

This project is built for training and learning purposes, do not use it for real use cases.

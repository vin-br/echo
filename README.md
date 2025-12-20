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

### Option B - Using Kubernetes with Minikube

Before you start:
- Make sure you have [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) installed
- Make sure you have [kubectl](https://kubernetes.io/docs/tasks/tools/) installed

For detailed Kubernetes deployment instructions, see [k8s/README.md](k8s/README.md)

```shell
# Start Minikube and deploy the app:
minikube start
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/

# Access the application (may take a minute for model to load)
minikube service arc-backend -n arc
```

### Option C - Using Vagrant + Ansible (IaC)

Before you start, make sure you have the following installed:
- [Vagrant](https://www.vagrantup.com/downloads), 
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)

For detailed instructions, see [iac/README.md](iac/README.md)

```shell
# Navigate to the iac directory
cd iac

# Start and provision the VM
vagrant up

# This will:
# - Create a Fedora 40 VM
# - Install Python 3.14.2 and dependencies using uv
# - Start the application as a systemd service
# - Run a health check

# Access the application at:
http://localhost:8080

# Or re-run Ansible without recreating the VM
vagrant provision

# Common commands:
vagrant halt      # Stop the VM
vagrant ssh       # Connect to the VM
vagrant destroy   # Delete the VM
```

Starting the ARC VM with Vagrant should look like this:

![Terminal `vagrant up`](screenshots/arc-vm-1-vagrant.png){width=100% height=auto}
![Terminal `vagrant provision`](screenshots/arc-vm-2-vagrant.png){width=100% height=auto}

### Option D - Local Developer setup

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

## Swagger API Documentation

The API documentation is automatically generated using FastAPI and can be accessed via Swagger UI at the following URL when the application is running:

```shell
# Swagger UI
http://localhost:8000/docs
```

## CI/CD Pipeline

The project uses **GitLab CI/CD** with 3 stages:
- **Lint** → Runs `ruff` on Python code
- **Test** → Runs `pytest` on backend
- **Build** → Builds and pushes Docker images to GitLab Container Registry

**Quick Setup:**

```shell
# 1. Push to GitLab
git remote add gitlab https://gitlab.com/vin-br/arc.git
git push gitlab main

# 2. Configure CI/CD Variables
# Go to Settings → CI/CD → Variables and add:
# - CI_REGISTRY: registry.gitlab.com
# - CI_REGISTRY_USER: Your GitLab username
# - CI_REGISTRY_PASSWORD: Personal access token (with api, read_registry, write_registry scopes)
```

For detailed CI/CD setup including troubleshooting and maintenance, see [GITLAB_CI_SETUP.md](GITLAB_CI_SETUP.md)

## Unit testing

```shell
# Run Tests from root with verbose output
uv run pytest backend/tests/ -v --tb=auto

# Run Test Coverage with a report in the terminal
uv run pytest backend/tests/ --cov=backend/app --cov=ai --cov-report=term-missing

# Run Test Coverage with an HTML report
uv run pytest --cov=backend --cov-report=html
```

## Monitoring Containers with Netdata Container

To monitor the Docker containers running the ARC application, you can use Netdata Container. It is started with the Docker Compose setup and provides real-time monitoring of system and application metrics.

![Netdata Dashboard](screenshots/arc-monitoring-netdata.png){width=100% height=auto}

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
- [Kubernetes Docs](https://kubernetes.io/docs/home/)
- [Minikube Docs](https://minikube.sigs.k8s.io/docs/)
- [Vagrant Docs](https://developer.hashicorp.com/vagrant/docs)
- [Vagrant Fedora 40 Bento Box](https://portal.cloud.hashicorp.com/vagrant/discover/bento/fedora-40)
- [Netdata Docs](https://learn.netdata.cloud/docs/agent/packaging/docker)

## Disclamer

This project is built for training and learning purposes, do not use it for real use cases.

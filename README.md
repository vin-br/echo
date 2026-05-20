# ARC
[![GitLab](https://img.shields.io/badge/GitLab-Repository-ff6d28?style=for-the-badge&logo=gitlab&logoColor=white&logoWidth=20)](https://gitlab.com/vin-br/arc) [![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github&logoColor=white&logoWidth=20)](https://github.com/vin-br/arc) [![Docker](https://img.shields.io/badge/Docker-Repository-2396ed?style=for-the-badge&logo=docker&logoColor=white&logoWidth=20)](https://hub.docker.com/u/vinbr) [![CI/CD](https://img.shields.io/gitlab/pipeline/vin-br/arc/main?style=for-the-badge&logo=gitlab&logoColor=white&label=CI%2FCD)](https://gitlab.com/vin-br/arc/-/pipelines?ref=main) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0e76a8?style=for-the-badge&logo=linkedin&logoColor=white&logoWidth=20)](https://www.linkedin.com/in/vin-br/)

ARC stands for **Augment**, **Recognize**, **Classify** — and that's the exact pipeline it runs. It's a computer vision application I built to automatically detect and annotate brain tumors on MRI scans.

---

## Demo

Check out this [video](demo.mp4) for a demonstration on how to start and use the app.

## Overview

<figure style="max-width:auto;margin:0 auto;">
  <img src="screenshots/app-overview-1.png" alt="Arc App Overview - Homepage" style="width:auto;height:auto;display:block;">
  <figcaption style="text-align:center;font-size:0.95rem;color:#555;margin-top:0.5rem;">ARC Homepage — ARC main landing with upload and predictions</figcaption>
</figure>

---

<figure style="max-width:auto;margin:0 auto;">
  <img src="screenshots/app-overview-2.png" alt="Arc App Overview - Image uploaded and shown" style="width:auto;height:auto;display:block;">
  <figcaption style="text-align:center;font-size:0.95rem;color:#555;margin-top:0.5rem;">ARC Image Uploaded — Displaying the uploaded MRI image</figcaption>
</figure>

---

<figure style="max-width:auto;margin:0 auto;">
  <img src="screenshots/app-overview-3.png" alt="Arc App Overview - Prediction" style="width:auto;height:auto;display:block;">
  <figcaption style="text-align:center;font-size:0.95rem;color:#555;margin-top:0.5rem;">ARC Prediction — Model prediction displayed with confidence score</figcaption>
</figure>

---

## Use Case

<figure style="max-width:auto;margin:0 auto;">
  <img src="screenshots/app-use-case-1.png" alt="Arc App - Upload Case Focus without an MRI" style="width:auto;height:auto;display:block;">
  <figcaption style="text-align:center;font-size:0.95rem;color:#555;margin-top:0.5rem;">ARC App - Upload Case Focus</figcaption>
</figure>

---

<figure style="max-width:auto;margin:0 auto;">
  <img src="screenshots/app-use-case-2.png" alt="Arc App - Upload Case Focus with an MRI" style="width:auto;height:auto;display:block;">
  <figcaption style="text-align:center;font-size:0.95rem;color:#555;margin-top:0.5rem;">ARC App - Upload Case Focus with an MRI</figcaption>
</figure>

---

<figure style="max-width:auto;margin:0 auto;">
  <img src="screenshots/app-use-case-3.png" alt="Arc App - Prediction Case Focus" style="width:auto;height:auto;display:block;">
  <figcaption style="text-align:center;font-size:0.95rem;color:#555;margin-top:0.5rem;">ARC App - Prediction Case Focus</figcaption>
</figure>

---

### Project Structure

```
├── vision/                 # Vision model training (PyTorch)
├── backend/                # FastAPI backend API
├── data/                   # Dataset files
├── frontend/               # SvelteKit frontend (Bun)
├── iac/                    # Infrastructure as Code (Vagrant + Ansible)
├── k8s/                    # Kubernetes deployment manifests
├── models/                 # Pre-trained model weights
├── nginx/                  # Nginx reverse proxy configs (prod + dev)
├── screenshots/            # Screenshots and visual assets
├── scripts/                # Utility scripts
├── docker-compose.yaml     # Docker Compose configuration
├── docker-compose.dev.yaml # Docker Compose for development
├── docker-dev.sh           # Convenience wrapper for dev compose
├── .gitlab-ci.yml          # GitLab CI/CD pipeline configuration
├── README.md               # Project documentation
└── ...                     # Other configuration and resource files
```    

---

### Technical Stack

- **AI Model:** Convolutional Neural Network (ConvNeXt) using PyTorch
- **Backend:** FastAPI
- **Frontend:** SvelteKit with Bun
- **Reverse Proxy:** Nginx
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Kubernetes (Minikube for local development)
- **Infrastructure as Code (IaC):** Vagrant + Ansible
- **CI/CD:** GitLab CI/CD (Docker Hub + GitLab Container Registry)
- **Versioning:** CalVer (YY.MM)

---

### Environment Variables

The frontend requires a `BACKEND_URL` environment variable so the SvelteKit server can reach the backend API during SSR.

- **Docker:** Set automatically via `environment:` in docker-compose — no `.env` file needed.
- **Local dev:** Copy `frontend/.env.example` to `frontend/.env` and set `BACKEND_URL=http://localhost:8000`.

---

##  Installation Options

### Option A - Using Public Docker Hub Images

**Using Pre-built Docker Images**
Public images are available on Docker Hub for easy user setup:
- [ARC Vision on Docker Hub](https://hub.docker.com/r/vinbr/arc-vision)
- [ARC Backend on Docker Hub](https://hub.docker.com/r/vinbr/arc-backend)
- [ARC Frontend on Docker Hub](https://hub.docker.com/r/vinbr/arc-frontend)

<img src="screenshots/docker-hub-repositories.png" alt="Docker Hub Repositories with ARC AI and Backend Images" style="max-width:auto;height:auto;">

Before you start:
- make sure you have [Docker](https://www.docker.com/get-started/) installed on your machine.

```shell
# Clone the repository (SSH or HTTPS):
git clone git@gitlab.com:vin-br/arc.git # SSH
git clone https://gitlab.com/vin-br/arc.git # HTTPS

# From root directory, pull and start the containers:
docker compose up -d

# The images will be automatically pulled from Docker Hub on first run
# Access the app via Nginx at:
http://localhost:8080
```

The app should now be running locally on your machine through Docker containers.

> The Docker backend image includes the necessary model weights, so no additional download is required.

<img src="screenshots/docker-compose.png" alt="Docker Compose Prod Terminal Overview" style="max-width:auto;height:auto;">

<img src="screenshots/docker-containers.png" alt="Docker Containers in Docker Desktop" style="max-width:auto;height:auto;">

```shell
# To stop the containers, run:
docker compose down

# To update to the latest images:
docker compose pull
docker compose up -d
```

--- 

### Option B - Using Docker Developer Setup

Before you start:
- make sure you have [Docker](https://www.docker.com/get-started/) installed on your machine.
- make sure you have [Git LFS](https://git-lfs.github.com/) installed to download model files.

```shell
# Clone the repository with SSH:
git clone git@gitlab.com:vin-br/arc.git
cd arc

# Pull the model files using Git LFS because they were too large for regular Git:
git lfs pull # requires Git LFS installed

# From root directory, build and start the development containers:
./docker-dev.sh up --build
# Or without the wrapper:
docker compose -f docker-compose.dev.yaml up --build

# This will:
# - Build images locally from Dockerfiles
# - Mount local code for live reload during development
# - Use local model files from ./models directory

# Access the app via Nginx at:
http://localhost:8081
```

<img src="screenshots/docker-compose-dev.png" alt="Docker Compose Development Terminal Overview" style="max-width:auto;height:auto;">

---

<img src="screenshots/docker-containers-dev.png" alt="Docker Containers in Docker Desktop" style="max-width:auto;height:auto;">

```shell
# To stop the containers, run:
docker compose -f docker-compose.dev.yaml down

# To rebuild without cache:
docker compose -f docker-compose.dev.yaml build --no-cache
```

**Developer setup includes:**
- Live code reloading (code changes reflect immediately)
- Local model weights for testing different versions
- Access to source code for debugging

---

### Option C - Using Kubernetes with Minikube

Before you start:
- Make sure you have [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) installed
- Make sure you have [kubectl](https://kubernetes.io/docs/tasks/tools/) installed

For detailed Kubernetes deployment instructions, see [k8s/README.md](k8s/README.md)

```shell
# # From root directory, start and deploy:
minikube start
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

<img src="screenshots/minikube-start-deploy.png" alt="Minikube Start and Deploy Terminal Overview" style="max-width:auto;height:auto;">

```shell
# Check deployment status
# Verify that the backend and AI pods are running before continuing
kubectl get all -n arc

# Access the application
# Note: Backend may take a minute to load the ML model on first startup
# Be patient!

# Using minikube service (tested with Docker driver on macOS)
minikube service arc-nginx -n arc
# This will open your browser automatically
```


<img src="screenshots/minikube-service.png" alt="Minikube Service Terminal Overview" style="max-width:auto;height:auto;">

---

### Option D - Using Vagrant + Ansible (IaC)

Before you start, make sure you have the following installed:
- [Vagrant](https://www.vagrantup.com/downloads)
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
# - Install Python 3.14.5 and dependencies using uv
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

<img src="screenshots/vagrant-vm-1.png" alt="Terminal `vagrant up` command" style="max-width:auto;height:auto;">

<img src="screenshots/vagrant-vm-2.png" alt="Terminal `vagrant provision` command" style="max-width:auto;height:auto;">

### Option E - Local Developer setup

**Installation steps to set up the project locally using uv:**

Before you start:
- make sure you have curl installed on your machine if you are on macOS/Linux.
- make sure you have [Bun](https://bun.sh/) installed for the frontend.
- make sure you have [Git LFS](https://git-lfs.github.com/) installed to download model files.

```shell
# clone the repository with SSH:
git clone git@gitlab.com:vin-br/arc.git
cd arc

# Pull the model files using Git LFS because they were too large for regular Git:
git lfs pull # requires Git LFS installed

# Install uv (on macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or alternatively on Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# if uv install fails, check the documentation at https://docs.astral.sh/uv/ for other installation methods.

# From root directory, install Python 3.14.5 with uv:
uv python install 3.14.5

# Install backend dependencies:
cd backend
uv sync --group dev
cd ..

# Install frontend dependencies:
cd frontend
bun install
cd ..
```

**Run the backend:**
```shell
cd backend
uv run uvicorn app.main:app --reload
```

**Run the frontend (in another terminal):**
```shell
cd frontend
BACKEND_URL=http://localhost:8000 bun run dev
```

<img src="screenshots/uvicorn-run-dev.png" alt="Uvicorn Run Terminal Overview" style="max-width:auto;height:auto;">

The app should now be running locally — backend at `http://localhost:8000` and frontend at `http://localhost:5173`.

## Swagger API Documentation

The API documentation is automatically generated using FastAPI and can be accessed via Swagger UI at the following URL when the application is running:

```shell
# Swagger UI
http://localhost:8000/docs
```

<img src="screenshots/app-swagger-ui.png" alt="Swagger UI showing full API documentation" style="max-width:auto;height:auto;">

---

## CI/CD Pipeline

The project uses **GitLab CI/CD** with 3 stages:
1. **Lint** → Runs `ruff` on Python code
2. **Test** → Runs `pytest` on backend
3. **Build** → Builds and pushes Docker images to Docker Hub and GitLab Container Registry

On develop branch, only Lint and Test stages run.
On main branch, all 3 stages run.

<img src="screenshots/cicd-steps.png" alt="GitLab CI/CD Steps Overview" style="max-width:auto;height:auto;">

**Setup:**

```shell
# 1. Push to GitLab
git remote add gitlab https://gitlab.com/vin-br/arc.git
git push gitlab main

# 2. Configure CI/CD Variables
# Go to Settings → CI/CD → Variables and add:
# - CI_REGISTRY: registry.gitlab.com
# - CI_REGISTRY_USER: GitLab username
# - CI_REGISTRY_PASSWORD: Personal access token (with api, read_registry, write_registry scopes)
```

<figure style="max-width:auto;margin:0 auto;">
  <img src="screenshots/cicd-main-validation.png" alt="GitLab CI/CD Main Branch Validation Overview" style="width:auto;height:auto;display:block;">
  <figcaption style="text-align:center;font-size:0.95rem;color:#555;margin-top:0.5rem;">GitLab CI/CD main branch validation overview</figcaption>
</figure>

---

<figure style="max-width:auto;margin:0 auto;">
  <img src="screenshots/cicd-develop-validation.png" alt="GitLab CI/CD Develop Branch Validation Overview" style="width:auto;height:auto;display:block;">
  <figcaption style="text-align:center;font-size:0.95rem;color:#555;margin-top:0.5rem;">GitLab CI/CD develop branch validation overview</figcaption>
</figure>

---

<figure style="max-width:auto;margin:0 auto;">
  <img src="screenshots/cicd-merge-pipeline.png" alt="GitLab CI/CD Merge Pipeline Overview" style="width:auto;height:auto;display:block;">
  <figcaption style="text-align:center;font-size:0.95rem;color:#555;margin-top:0.5rem;">GitLab CI/CD Merge pipeline overview when merging devops branch into develop branch</figcaption>
</figure>

---

## Unit testing

```shell
# Run Tests from root with verbose output
uv run pytest backend/tests/ -v --tb=auto
```

<img src="screenshots/pytest-run.png" alt="Pytest Run Terminal Overview" style="max-width:auto;height:auto;">


```shell
# Run Test Coverage for the backend with a report in the terminal
uv run pytest backend/tests/ --cov=backend/app --cov-report=term-missing
```

<img src="screenshots/pytest-coverage.png" alt="Pytest Coverage Terminal Overview" style="max-width:auto;height:auto;">


```shell
# Run Test Coverage with an HTML report
uv run pytest --cov=backend --cov-report=html
```

<img src="screenshots/pytest-html.png" alt="Pytest HTML Overview" style="max-width:auto;height:auto;">

---

## Monitoring Containers with Netdata Container

To monitor the Docker containers running the ARC application, you can use Netdata Container. It is started with the Docker Compose setup and provides real-time monitoring of system and application metrics.

<img src="screenshots/netdata-monitoring-1.png" alt="Netdata Homepage" style="max-width:auto;height:auto;">

<img src="screenshots/netdata-monitoring-2.png" alt="Netdata Dashboard" style="max-width:auto;height:auto;">

---

## Model Metrics

Table overview of model performance metrics available in the app:

<img src="screenshots/metrics-leaderboard.png" alt="GitLab CI/CD Main Branch Validation Overview" style="max-width:auto;height:auto;">

These metrics are stored in a DuckDB database located in the folder `backend/data/metrics.duckdb`.

## Versioning

Versioning follows CalVer: `YY.MM` where YY.MM reflects when the work was done. A patch suffix (e.g. `26.05.1`) is added only for subsequent fixes within the same month. For example, version `26.05` indicates that the work was completed in May 2026.

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
- [DuckDB](https://duckdb.org/docs/stable/)
- [Git LFS](https://git-lfs.github.com/)
- [GitLab CI/CD Docs](https://docs.gitlab.com/ee/ci/)
- [pytest](https://docs.pytest.org/en/stable/)
- [uv](https://docs.astral.sh/uv/)
- [Ruff](https://docs.astral.sh/ruff/)
- [Ty](https://docs.astral.sh/ty/)
- [Docker](https://docs.docker.com/manuals/)
- [Kubernetes Docs](https://kubernetes.io/docs/home/)
- [Minikube Docs](https://minikube.sigs.k8s.io/docs/)
- [Vagrant Docs](https://developer.hashicorp.com/vagrant/docs)
- [Vagrant Fedora 40 Bento Box](https://portal.cloud.hashicorp.com/vagrant/discover/bento/fedora-40)
- [Netdata Docs](https://learn.netdata.cloud/docs/agent/packaging/docker)

## Disclamer

This project is built for training and learning purposes, do not use it for real use cases.

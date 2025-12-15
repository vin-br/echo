# Project To-Do List

---

## FastAPI Backend

### Testing

- [ ] Unit tests for model inference and data preprocessing
- [ ] API-level tests covering endpoints: `GET /`, `GET /healthz`, `GET /api/metrics`
- [	] Configuration tests validating required paths
- [	] Database tests for DuckDB ingestion and retrieval operations
- [	] Inference tests ensuring PyTorch model produces valid predictions
- [ ] Health-check regression test

## DevOps

## Docker

- [x] Create Dockerfiles for backend, frontend, and PyTorch training (slim base images, health checks)
- [x] Produce multi-service `docker-compose.yml` for local dev parity
- [ ] Document required env vars and developer experience (live reload)
- [ ] Push versioned images to Docker Hub
- [ ] Reference Docker Hub links in `README.md`
  
### CI/CD

- [ ] Configure GitLab CI/CD pipeline (`.gitlab-ci.yml`)
  - [ ] Lint stage (code formatting, static checks)
  - [ ] Test stage (pytest suite with coverage reporting)
  - [ ] Build stage (Docker image builds)
  - [ ] Security checks (container scan, dependency audit)
- [ ] Gate merge requests on passing CI
- [ ] Document pipeline badges and status in `README.md`

### Kubernetes

- [ ] Add local Minikube cluster and document prerequisites
- [ ] Add K8s manifests:
  - [ ] Deployments for FastAPI and frontend
  - [ ] Services for load balancing
  - [ ] PersistentVolume and PersistentVolumeClaim for data persistence
  - [ ] ConfigMap/Secret for runtime settings and credentials
- [ ] Add readiness and liveness probes
- [ ] Document K8s deployment walkthrough in `README.md`

**K8s tasks possible**

- [ ] Implement rolling updates and rollbacks (`kubectl rollout` task)
- [ ] Secret and ConfigMap management for credential rotation
- [ ] Horizontal Pod Autoscaler (HPA) for FastAPI workload
- [ ] Job/CronJob for periodic PyTorch model retraining
- [ ] Service load-balancing configuration
- [ ] Implement Istio service mesh for traffic shifting between versions
- [ ] Add Istio security tasks (mutual TLS, authorization policies)

### Infrastructure as Code using Ansible

- [ ] Create Vagrant or Multipass VM definition for single Linux node (macOS alternative)
- [ ] Write Ansible playbooks to:
  - [ ] Install Python runtime and dependencies
  - [ ] Install and configure database (DuckDB/PostgreSQL/Redis)
  - [ ] Deploy FastAPI application
  - [ ] Run health checks via synced folder
- [ ] Automate Ansible inventory and vars for reproducible provisioning
- [ ] Document IaC setup instructions in `README.md`

### DevOps Documentation

- [ ] Expand `README.md` with:
  - [ ] Overview of the project and features
  - [ ] Install/setup instructions (with commands)
  - [ ] Usage instructions (local dev, Docker Compose, Kubernetes)
  - [ ] Testing instructions (how to run pytest suite)
  - [ ] Links to Docker Hub images
  - [ ] CI/CD pipeline badges and status
  - [ ] IaC/K8s deployment walkthroughs
  - [ ] Screenshots folder with evidence (UI, CI runs, Ansible output, K8s resources)

---

## SvelteKit Frontend

- [ ] Start migrating to SvelteKit while preserving existing HTML/CSS/JS
	- [ ] Set up SvelteKit project structure
	- [ ] Integrate existing HTML/CSS/JS into Svelte components
	- [ ] Ensure communication with FastAPI backend works correctly

---

## PyTorch Model

- [ ] Train and test more models to ensure comparable performance with the Keras model or even better performance
	- [ ] Experiment with different models
	- [ ] Tune hyperparameters (learning rate, batch size, epochs)
- [ ] Explore more plots and metrics to better evaluate the models

# Changelog

---

Summary of changes made to the Echo project.

Versioning follows CalVer: `YY.MM.PATCH` — where `YY.MM` reflects when the work was done and `PATCH` is incremented for each subsequent release within the same month.

## [26.05.2] - 2026-05-24

### Added
- `vision/detection/` package: YOLOv8 fine-tuning engine and CLI (`ultralytics`).
- Optuna hyperparameter search as the default classification training pipeline — searches `lr` and `batch_size`; explicit `--lr` + `--batch-size` args skip the search.
- `automate/`: carousel GIF generation, leaderboard screenshot target, plot regeneration on startup.
- `scripts/enhance_dataset.py`: dataset balancing pipeline (perceptual dedup, quality filtering, augmentation).
- Three new classification architectures: Swin-V2-T, MaxViT-T, ConvNeXt-Small.
- Root `pyproject.toml` aggregating all subpackage dependencies for single-install dev setup.

### Changed
- Restructured `vision/` into `classification/`, `detection/`, and `common/` subpackages.
- Moved shared modules (`config.py`, `paths.py`, `visualize.py`) into `vision/common/`.
- Reorganized `data/` into `data/classification/` (tracked) and `data/detection/` (gitignored, downloadable).
- Merged leaderboard and training curves into a single "Transparency" section in the frontend.
- Leaderboard card: single overview with Test Accuracy, Test Recall, and Test Macro F1 columns.
- Docker Compose dev: bind mounts replace named `results` volume.
- Detection model downloads to `models/detection/` instead of working directory.
- Backend Dockerfile: copies detection model checkpoint at build time.
- Plot filenames: replaced dots in learning rate notation with underscores (`8_823e-3` instead of `8.823e-3`) to avoid filename issues.
- License changed from MPL 2.0 to Apache 2.0.
- GitHub Copilot instructions added.
- CI/CD: use `CI_JOB_TOKEN` for GitLab Container Registry auth.
- Version bump to `26.05.2`.

### Removed
- `--tune` flag from classification CLI (Optuna is now the default; no flag needed).
- `vision/classification/evaluate.py` — dead code, never imported.
- `confusion_matrix_count_plot` and `confusion_matrix_distrib_plot` from `vision/visualize.py` — unused.
- `k8s/vision-deployment.yaml` and `k8s/vision-service.yaml` — vision runs now as a batch job, not a service.
- `scripts/find_duplicates.py` and `scripts/rename_files.py` — functionality subsumed by `enhance_dataset.py`.


## [26.05.1] - 2026-05-21

### Added
- `automate/` service: Playwright + Firefox automation for README screenshots and GIFs.
- `GET /api/latency` endpoint with DuckDB-persisted rolling average (survives restarts).
- Ansible Docker connection plugin for IaC provisioning (replaces Vagrant/VirtualBox).

### Changed
- README restructured with table of contents, collapsible sections, and GIF assets.
- Renamed `screenshots/` to `media/`.
- Removed Vagrant/VirtualBox legacy from IaC.
- `htmlcov/` output moved to `backend/htmlcov/`.
- Version bump to `26.05.1` across all packages.
- Removed demo.mp4 from the repo and added instructions to generate gifs instead with the new automation service.

## [26.05] - 2026-05-20

### Added
- Migrated frontend from Jinja2 HTML/CSS to SvelteKit 5 with Bun.
- Frontend Dockerfile using `oven/bun` multi-stage build.
- Frontend services in both `docker-compose.yaml` and `docker-compose.dev.yaml`.
- New `POST /api/predict` JSON endpoint on the backend.
- `docker-dev.sh` and `docker.sh` convenience wrappers for Docker Compose.
- Nginx reverse proxy for both prod (`:8080`) and dev (`:8081`).
- GitLab Container Registry push alongside Docker Hub in CI/CD.
- CalVer tags for Docker images (`:26.05` + `:latest`).
- Frontend build job in CI/CD pipeline.
- Kubernetes resources for frontend (deployment + service) and nginx reverse proxy (deployment + service + configmap).

### Changed
- Backend is now a pure JSON API (removed Jinja2 template rendering and static file serving).
- Adopted CalVer `YY.MM` versioning across all packages (patch suffix only when needed).
- Renamed `ai/` to `vision/` for clarity.
- Removed `shared/` module — config and paths are now service-local in `backend/app/` and `vision/`.
- Replaced Font Awesome CDN with inline SVGs.
- Decoupled backend from vision container — vision results are baked into the prod image and shared via a named Docker volume in dev.
- Updated Python from 3.14.2 to 3.14.5 across Dockerfiles and CI.
- Updated all dependencies to latest versions.
- Kubernetes backend service changed from NodePort to ClusterIP (nginx is now the single entry point).
- Added `proxy_buffering off` to dev nginx config to prevent temp file warnings.
- Updated CI/CD pipeline: `ai/` → `vision/`, removed `shared/` from lint paths.
- Updated backend tests for JSON API responses.
- Updated README with new project structure, tech stack, and URLs.

## [25.12.1] - 2025-12-21

### Added
- Model inference and data preprocessing endpoints.
- Interactive API documentation (Swagger UI).
- Model leaderboard in the UI to compare model performance and pick the best model.
- Simplified local developer and contributor setup with different install possibilities (Docker, Kubernetes, IaC, local venv with uv).
- Added Netdata monitoring for container health and performance metrics.
- Added models with git LFS support for easier management of large files.

### Changed
- Frontend improvements for a better user experience (improved upload flow, notifications, and layout tweaks).
- Increased backend test coverage and CI/CD automation to improve reliability.
- Updated dependencies to latest stable versions and refactored codebase.
- Updated documentation and assets.

## [25.12] - 2025-12-04
- Migrated the training pipeline to PyTorch and replaced the legacy Keras workflow.
- Added new PyTorch model checkpoints plus a CLI trainer that saves checkpoints, metrics, and history files.

## [25.11] - 2025-11-29
- Added FastAPI backend skeleton to serve the application shell.
- Created initial HTML/CSS frontend to interact with the backend endpoints.

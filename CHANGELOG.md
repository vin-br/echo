# Changelog

---

Summary of changes made to the Arc project.

Versioning follows CalVer: `YY.MM` where YY.MM reflects when the work was done. A patch suffix (e.g. `26.05.1`) is added only for subsequent fixes within the same month.

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

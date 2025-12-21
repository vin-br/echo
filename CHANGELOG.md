# Changelog

---

Summary of changes made to the Arc project.

## [0.1.0] - 2025-12-21

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

## [0.0.2] - 2025-12-04
- Migrated the training pipeline to PyTorch and replaced the legacy Keras workflow.
- Added new PyTorch model checkpoints plus a CLI trainer that saves checkpoints, metrics, and history files.

## [0.0.1] - 2025-11-29
- Added FastAPI backend skeleton to serve the application shell.
- Created initial HTML/CSS frontend to interact with the backend endpoints.

---
applyTo: "models/**/*.pt"
---

# Git LFS

- All `.pt` model files under `models/` are tracked by Git LFS (see `.gitattributes`).
- After cloning, run `git lfs install && git lfs pull` to fetch model binaries.
- Adding a model: place `.pt` file in `models/classification/` or `models/detection/` — LFS tracking is automatic via the glob pattern.
- Removing a model: use `git rm <path>` then commit. Do **not** delete the file manually.
- If `git push` fails with "git-lfs not found", run `git lfs install --force` to refresh hooks, then ensure `git-lfs` is on PATH (`brew install git-lfs` on macOS).
- **VS Code Source Control**: VS Code's git UI uses the system PATH (not the terminal's). If LFS fails only in VS Code but works in terminal, symlink: `sudo ln -sf /opt/homebrew/bin/git-lfs /usr/local/bin/git-lfs`

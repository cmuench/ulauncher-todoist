# Repository Guidelines

## Project Structure & Module Organization
- `main.py` bootstraps the Ulauncher extension by loading `todoistext/TodoistExtension`.
- `todoistext/` holds the extension logic, split into listeners (`*EventListener.py`), task lists, and the Todoist API wrapper. Keep new feature modules here.
- `doc/` and `images/` store documentation assets; update screenshots alongside UI changes.
- `manifest.json`, `requirements.txt`, and `versions.json` define the extension metadata, dependencies, and compatibility—validate edits against Ulauncher requirements.

## Build, Test, and Development Commands
- `make lint` runs Pylint across every Python file.
- `make format` applies yapf formatting recursively; run before committing.
- `make deps` installs runtime dependencies with `pip3` (requires sudo in most setups).
- `make link` symlinks this checkout into the local Ulauncher extensions directory; follow with `ulauncher -v` to reload.
- `make dev` starts Ulauncher in dev mode without other extensions for faster iteration.

## Coding Style & Naming Conventions
- Target Python 3 with 4-space indentation and yapf’s default style; avoid tabs.
- Use snake_case for functions and variables, CapWords for classes, and module-level constants in UPPER_SNAKE_CASE.
- Keep listener classes focused on one concern and prefer small helper functions within the same module when logic grows.
- Add concise docstrings when behavior is non-obvious, especially around Todoist API interactions.

## Testing Guidelines
- No automated test suite exists; validate behavior manually via `make link` followed by `ulauncher --no-extensions --dev -v`.
- Exercise command keywords (`todo`, project-specific queries) and confirm task creation against a sandbox Todoist account.
- Capture regression steps in the PR description if the change affects user-visible flows.

## Commit & Pull Request Guidelines
- Follow the existing Git history: short, imperative commit subjects (e.g., “Fix task creation”).
- Include a clear summary, test notes, and relevant issue links in pull requests; screenshots or GIFs are expected for UI-facing changes.
- Ensure the manifest, README, and screenshots stay aligned with new features before requesting review.

## Configuration Notes
- Store Todoist API tokens in the extension preferences panel; never commit secrets.
- If new settings are added, document keys in `manifest.json` and mention them in `README.md` and user-facing release notes.

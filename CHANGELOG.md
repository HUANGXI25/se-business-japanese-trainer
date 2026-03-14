# Changelog

All notable changes to this project will be documented in this file.

The format is intentionally lightweight and focused on changes that matter to maintainers and contributors.

## [0.1.0] - 2026-03-14

First public-ready OSS baseline.

### Added

- Local-first FastAPI Web MVP for Japanese business communication training
- 21 built-in SE roleplay scenarios stored in `data/scenarios.json`
- Learning mode and practice mode
- Rules-based scoring, correction, recommendation, mistake notes, records, and analytics
- Open source project docs: `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`
- Architecture and roadmap docs under `docs/`
- Minimal pytest suite and GitHub Actions test workflow

### Changed

- Repository hygiene improved with `.gitignore` and removal of tracked local artifacts
- SQLite database is initialized automatically on first run
- README updated for public OSS positioning and contributor onboarding
- Template response usage updated to current FastAPI / Starlette style
- Timestamp defaults updated to avoid deprecated UTC helpers

### Notes

- This release is still an MVP.
- Feedback quality is rules-based and intentionally explainable.
- Test coverage is intentionally small and focused on core smoke paths.

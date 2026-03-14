# Public Release Checklist

## Documentation

- [ ] README reflects current project state
- [ ] Architecture and roadmap docs are present
- [ ] License, contributing, and security policy are present

## Local Run Verification

- [ ] `pip install -r requirements.txt`
- [ ] `uvicorn main:app --reload`
- [ ] Home page opens successfully
- [ ] One training flow can be completed locally

## Test Status

- [ ] `python -m pytest -q` passes
- [ ] GitHub Actions workflow file is present

## Repository Hygiene

- [ ] `.gitignore` covers local artifacts
- [ ] No local database, cache, or virtualenv files are staged
- [ ] No secrets or private data are included

## v0.1.0 Tag Readiness

- [ ] Changelog updated
- [ ] Release notes draft reviewed
- [ ] Current branch is in a clean, reviewable state

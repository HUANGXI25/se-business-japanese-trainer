# Codex for OSS Application Draft

## Project

Business Japanese SE Roleplay Trainer

## One-line Project Introduction

A local-first web trainer for practicing Japanese business communication in realistic entry-level SE workplace scenarios.

## Maintainer Role

I am maintaining this repository as an actively evolving open source MVP.

My role is to:

- keep the project runnable locally
- improve the quality and realism of scenario-based feedback
- make the repository easier for outside contributors to understand and extend
- gradually turn a personal prototype into a stable, publicly maintainable OSS project

## Why This Repository Is Worth Sustaining

This repository sits at the intersection of language learning, workplace communication, and developer tooling.

Its value comes from being:

- focused on a real user problem rather than generic chat
- local-first and usable without paid API dependencies
- explainable, because feedback comes from visible rules and scenario structure
- extensible, because scenarios, scoring logic, correction logic, and future LLM integration are already separated

It is worth sustaining because the project can grow in two directions without losing focus:

1. Better training quality for Japanese business communication in SE contexts
2. Better contributor ergonomics for rules, scenarios, and lightweight educational tooling

## Current Project State

- The project is currently an MVP
- It runs locally with FastAPI, SQLite, Jinja2, and vanilla JavaScript
- It includes built-in scenarios, two training modes, rules-based scoring, mistake notes, records, and lightweight analytics
- It already has minimal tests, CI, OSS docs, and release materials

This application draft intentionally does not claim any user, traffic, star, or download numbers.

## How Codex / API Credits Would Help

Codex support would be most useful for maintenance and quality iteration rather than scale.

I would use Codex or API credits to help with:

- expanding and reviewing scenario data while keeping structure consistent
- refining scoring and correction rules without collapsing into vague feedback
- improving maintainability docs, contributor guidance, and release materials
- generating and validating targeted tests for key training flows
- reviewing small refactors that improve clarity without forcing a full rewrite

## What I Would Not Use It For

- I would not use Codex support to fabricate product traction or inflate project maturity
- I would not make external API dependence mandatory for the repository to function
- I would not use it to replace the project’s current local-first baseline with a closed hosted workflow

## Why This Project Fits Codex for OSS

This project is a good fit for Codex for OSS because it is small enough to be improved quickly, but concrete enough that maintenance effort clearly matters.

The repository already has:

- a clear problem scope
- a real runnable codebase
- structured data and modular rule logic
- a plausible path for outside contributions

Codex support would directly improve repository quality, contributor onboarding, and the realism of the training experience.

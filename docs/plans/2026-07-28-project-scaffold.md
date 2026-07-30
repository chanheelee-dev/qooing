# Runnable Project Scaffold Implementation Plan

> **For agentic workers:** Execute task-by-task with test-driven development and fresh verification.

**Goal:** Deliver a runnable qooing vertical slice, finalized specification, and project-guided
technical handbook.

**Architecture:** A uv workspace contains isolated producer and FastAPI packages. A Bun/Vite React
frontend consumes a read-only Markdown bundle and POST-based SSE chat backed by Pydantic AI.
Production-like Docker images are joined through Compose and nginx.

**Tech Stack:** Python 3.14, uv, FastAPI, Pydantic AI, Ruff, ty, pytest, Bun, React, Vite, Bun test,
Docker Compose, nginx.

## Tasks

- [x] Finalize the scaffold specification and workspace foundations.
- [x] Implement bundle validation and deterministic index generation test-first.
- [x] Implement the wiki store, Pydantic AI agent, API, and SSE protocol test-first.
- [x] Implement the three-panel React shell and stream parser test-first.
- [x] Add the bilingual handbook, production-like containers, and full local verification.

## Global Constraints

- Use `uv` for every Python command and Bun for every frontend command.
- Preserve existing user-authored design edits.
- Keep the server stateless and the baby profile client-owned.
- Exclude accounts, databases, ingestion automation, CI, and deployment automation.

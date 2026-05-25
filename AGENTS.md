# AGENTS.md — Midas

This repository contains **Midas**, a minimal static site generator written in Python — not a website built with it.

## What this is

- A Python package (`src/midas/`) that turns markdown into static HTML.
- Ships with built-in Jinja2 templates, CSS, and a dev server.
- Users install this package and run `midas init` / `midas build` / `midas serve`.

## Key files

| File | Purpose |
|---|---|
| `src/midas/core.py` | Build engine, RSS, server |
| `src/midas/cli.py` | CLI entry point |
| `src/midas/defaults.py` | Default config + `midas.yaml` loader |
| `src/midas/templates/` | Built-in Jinja2 templates |
| `src/midas/static/style.css` | Built-in stylesheet |
| `src/midas/starter/` | Scaffold copied by `midas init` |
| `pyproject.toml` | Package metadata |

## Dev workflow

Install editable: `pip install -e .`

Then `midas --help` to test CLI changes.

Do not confuse the package code with a user's project — there is no `site/` or `_dist/` at the repo root unless you're testing a build inside the repo.

## Versioning and releases

- **Single source of truth:** The version is defined in `pyproject.toml` only. `src/midas/__init__.py` reads it at runtime via `importlib.metadata.version("midas-ssg")` — never hardcode the version there.
- **To release a new version:**
  1. Bump the `version` field in `pyproject.toml`
  2. Commit with message like `chore: bump version to X.Y.Z`
  3. Tag as `vX.Y.Z` and push the tag
- **Default bump is patch (Z in X.Y.Z).** If the user doesn't specify a version or bump type, only increment the patch number. For example, `0.1.15` → `0.1.16`.
- **Never reuse a version number** that has already been tagged or published to PyPI. Always bump to the next version.
- **Never delete and recreate a tag** for a version that was already pushed or published. If a release has issues, bump to a new version instead.

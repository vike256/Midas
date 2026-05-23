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

Do not confuse the package code with a user's project — there is no `content/` or `dist/` at the repo root unless you're testing a build inside the repo.

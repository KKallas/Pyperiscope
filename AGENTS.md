# Working on Pyperiscope itself

(For writing *automations* with Pyperiscope, see `src/pyperiscope/scaffold/AGENTS.md`,
which `pyperiscope init` copies into each automation project.)

## Map

```
src/pyperiscope/
  target/layer1-3     data+storage → matching with details → creation & validated edits
  session/layer1-4    setup+safety → seeing (strict find) → acting (computer-use verbs) → logs & failure bundle
  supervisor/layer1-3 run attempts in subprocesses → agent fix (claude/codex CLI) → escalation ladder + human wait
  input/              backend contract (base.py), key names (keys.py), macos/ layer1-3 (routing, mouse, keyboard)
  safety/             Esc-hold kill switch, overlay process, notifications
  server/             stdlib HTTP server, JSON API (targets.py, runs.py, routes.py), static/ UI (vanilla JS)
  cli/                argparse front end; target commands share server/targets.py (same validation)
  scaffold/           files `pyperiscope init` writes into automation projects
  manual/             operations manual (aircraft-manual style), copied into projects by init;
                      supervisor/layer2.py maps failure kinds to its QRH checklists.
                      Keep it in sync with behaviour; mark unbuilt parts [v2.1 PLANNED]
legacy/v1/            the Jupyter-era v1, kept for reference
```

## Conventions (Simple Software Dogmas)

- A growing class lives in `layer1.py … layerN.py`; each layer imports the previous one
  and subclasses it under the same name; the package `__init__` exports the last layer.
- Every Python module stays **≤ 100 lines**. Split by adding a layer or a helper module.
- Prefer the standard library (the web server is `http.server`, not a framework).
- Docstrings explain *why*; keep them in sync with the code.
- One test file per component in `tests/`; synthetic screens come from `tests/conftest.py`.

## Invariants — do not break

- A target action never picks "one of several": exactly one match or an error.
- Target edits are saved only after validating on a screenshot (`Target.validate`).
- Coordinates: targets/matches in screenshot **pixels**; input backends take screen
  **points**; `Shot.to_points` is the only bridge. Each saved PNG has a `<name>.png.json`
  sidecar with `origin` and `scale`.
- Every synthetic input event is stamped with `TAG`; the overlay window uses
  `NSWindowSharingNone` so it never appears in captures.
- A run stopped by Esc (exit 3) is never escalated to an agent.

## Run

```bash
uv venv && uv pip install -e ".[test]"
.venv/bin/python -m pytest
```
Live input needs macOS Accessibility + Input Monitoring for the launching app; check with
`pyperiscope doctor`.

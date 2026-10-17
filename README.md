# Pyperiscope v2

Visual automation for software that has no API — old business applications, hardware
control panels, terminal emulators — written as plain Python workflows by a coding agent
(Claude Code, OpenAI Codex) and **repaired by that agent when it breaks**. A human
operator is the last step, not the first.

```
workflow (Python)  ──fails──▶  agent fixes it (Opus 5.5 / Codex)  ──still fails──▶  human, in the web UI
       ▲                              │ validated target edits              │ validated target edits
       └──────── re-run from the failed step ◀──────────────────────────────┘
```

v1 (the Jupyter-notebook version) lives in [legacy/v1/](legacy/v1/) on this branch and on `main`.

**[Operations manual](src/pyperiscope/manual/README.md):** written like an aircraft manual,
for the crew of operators and LLM agents that run the bots. It covers limitations,
systems, normal procedures (building a workflow, transfer of control, shift handover,
reconciliation), a quick reference handbook of failure checklists, and a dispatch list.
`pyperiscope init` copies it into every automation project, and the fixing agent is
pointed to the right checklist for each failure.

## Core ideas

- **Targets** are small screen patches found by template matching, plus a click point.
- **Details** (up to 4 per target) are extra patches that must appear at a fixed offset
  from the main patch. Ten identical "Edit" buttons become one unique target once its
  row label is a detail.
- **Strict finding**: an action on a target needs *exactly one* match. Zero or several is
  an error with a screenshot, numbered candidates and scores — never a guess.
- **Validated edits**: every target change (by agent or human) is tested on the failure
  screenshot right away and kept only if the target then matches once, at the chosen spot.
- **Separate input**: in `isolated` mode, events go straight to the target app's process
  (`CGEventPostToPid` on macOS). The user's cursor and keyboard are untouched, so a person
  can keep working while the automation runs.
- **Safety**: a floating pill shows that automation is running (it is invisible to the
  screenshots), and **holding Esc for 3 seconds stops everything**.
- **Agent-shaped API**: Session verbs mirror Claude's computer-use actions (`left_click`,
  `type`, `key("ctrl+s")`, `scroll`, `left_click_drag`), and the CLI speaks JSON.

## Quick start (macOS)

```bash
uv venv && uv pip install -e .          # or: pip install -e .
pyperiscope init my-automations && cd my-automations
pyperiscope doctor                      # grant Screen Recording, Accessibility, Input Monitoring
pyperiscope serve                       # http://127.0.0.1:8765 — capture targets
```

Then ask your agent (it reads `AGENTS.md` in the project, which `init` writes):

> Write a workflow that opens the invoice app and enters the next row from invoices.csv.

and run it under the escalation ladder:

```bash
pyperiscope run invoice_entry           # agent = claude, model = claude-opus-5-5 (pyperiscope.json)
pyperiscope run invoice_entry --agent codex
pyperiscope run invoice_entry --input dry   # rehearse: find everything, click nothing
```

## A workflow

```python
from pyperiscope import Workflow

wf = Workflow(__file__, app="Legacy ERP")

@wf.step
def open_customer(s):
    s.wait_for("customers.list", timeout=10)
    s.left_click("customers.edit")        # must match exactly once (details make it unique)

@wf.step
def update_phone(s):
    s.wait_for("customer.form")
    s.triple_click("customer.phone")
    s.type("+372 555 0101")
    s.key("cmd+s")

if __name__ == "__main__":
    wf.main()
```

Steps are the unit of resume: after a fix, the run restarts at the step that failed.

## Project layout

```
pyperiscope.json      settings: input mode, agent + model, timeouts, kill-switch hold time
AGENTS.md, CLAUDE.md  instructions for the coding agent (API, CLI)
manual/               operations manual (limitations, procedures, QRH)
targets/<name>/       target.json + main.png + detail1..4.png
workflows/*.py        workflows
runs/<id>/            run.json, attempt-N/ (events.jsonl, failure.json, failure*.png), fix-N.md
screens/              screenshots, tests, zooms
```

## CLI

| command | |
|---|---|
| `init [dir]` · `doctor` · `serve [--host 0.0.0.0]` | set up, check permissions, web UI (token-protected off localhost) |
| `screenshot` · `zoom SHOT --box x,y,w,h` | capture; enlarged crop with a grid in real pixels (for agents) |
| `target list / show / test / create / add-detail / set / delete` | inspect and repair targets, always validated |
| `new-workflow NAME [--app APP]` · `run NAME` | scaffold; supervised run with the agent → human ladder |

## Status and roadmap

Working on macOS, tested (`pytest`): matching with details, validated edits, sessions,
failure reports, the supervisor ladder (agent → human), the web API and CLI, the
overlay (confirmed excluded from capture), Esc-hold logic.

Not yet verified on a real app: isolated clicks/keys via `CGEventPostToPid` (needs the
Accessibility permission). Some apps ignore events posted to their process; for those set
`"input": "shared"` (real cursor, restored afterwards, waits while the user moves it).

Next:
1. Live-verify isolated input against a few real apps; record which need `shared`.
2. Full-resolution Retina capture (currently captures at point resolution on macOS 26).
3. Windows backend: `PostMessage`/`SendInput` to the target HWND; Linux: XTest on a
   second MPX pointer (a truly separate cursor).
4. Per-window capture so the target app can sit behind other windows.

## Development

```bash
uv venv && uv pip install -e ".[test]" && .venv/bin/python -m pytest
```

Code follows [Simple Software Dogmas](https://github.com/KKallas/SimpleSoftwareDogmas):
classes grow in `layerN.py` files (each extends the previous; `__init__` exports the last),
modules stay under 100 lines, one test file per component. See [AGENTS.md](AGENTS.md).

License: BSD-3-Clause.

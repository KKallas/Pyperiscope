# Pyperiscope automation project

This folder automates software that has no API, by looking at the screen (template
matching) and sending mouse/keyboard input. You, the coding agent, build the workflows
and repair them when they fail. A human operator has final authority.

## Operations manual: read before acting

`manual/` is the operations manual. It is written like an aircraft manual, and its
procedures override anything else here:

| When | Read |
|---|---|
| always | `manual/1-limitations.md`: never exceed |
| building a workflow | `manual/3-normal-procedures.md` NP-2 |
| a run failed | `manual/4-qrh.md`: run the checklist for the failure `kind` |
| handing over to the operator | `manual/4-qrh.md` Q9 (what the note must say) |

The three rules: **when in doubt, stop · never guess which one · never enter a line twice.**

## Layout

```
pyperiscope.json      settings (input mode, agent, timeouts)
manual/               operations manual (limitations, procedures, QRH checklists)
targets/<name>/       target.json + main.png + detail1..4.png   (never hand-edit)
workflows/<name>.py   one workflow per file, steps run in order
screens/              screenshots (setup, tests, zooms)
runs/<id>/            run.json, attempt-N/{events.jsonl, failure.json, failure*.png}, fix-N.md
```

## Concepts

- **Target**: a *main patch* (small crop of a screenshot) + *click point* relative to it.
  Found with template matching at `confidence` (default 0.9).
- **Details** (max 4 per target): extra patches that must sit at a fixed offset from the
  main patch (± tolerance px). They make a target unique when the main patch repeats,
  e.g. one of ten identical "Edit" buttons → add the row's label as a detail.
- **Strict finding**: `s.find()` and every action on a target name require **exactly one**
  match. 0 → `TargetNotFound`, 2+ → `AmbiguousTarget`. Never "click the first one".
- **Validated edits**: every target change is tested on a screenshot and saved only if
  the target then matches exactly once, at the intended spot.
- **Coordinates**: target/screenshot coordinates are *pixels* of the screenshot (Retina =
  2× points). Session actions convert to screen points for you.

## Writing a workflow

```python
from pyperiscope import Workflow

wf = Workflow(__file__, app="TextEdit")   # app: process that receives isolated input

@wf.step
def open_app(s):
    s.open_app("TextEdit")
    s.wait_for("textedit.new_document", timeout=10)

@wf.step
def write_text(s):
    s.left_click("textedit.new_document")
    s.wait_for("textedit.empty_page")
    s.type("Hello from Pyperiscope\n")
    s.key("cmd+s")

if __name__ == "__main__":
    wf.main()
```

Session API (`s`), verbs follow computer-use naming. `where` = target name, a `Match`,
or `(x, y)` screen points; `offset=(dx, dy)` in points.

| call | does |
|---|---|
| `find(name, timeout=5)` / `wait_for(...)` | wait until exactly one match → `Match` (`.point`, `.box`, `.score`) |
| `find_all(name)` | all matches now (0..n), no waiting |
| `exists(name, timeout=0)` | ≥1 match within timeout → bool |
| `wait_gone(name, timeout=5)` | wait until no match |
| `left_click / double_click / triple_click / right_click / middle_click(where)` | click |
| `mouse_move(where)` · `left_click_drag(start, end)` · `scroll(where, "down", 3)` | pointer |
| `type(text)` (`\n` = Return, `\t` = Tab) · `key("ctrl+a")`, `key("Return", repeat=2)` | keyboard |
| `open_app(name)` · `wait(seconds)` · `screenshot()` · `log(event, **data)` | misc |

Rules for good workflows:
- **Each step starts by waiting for a screen state it recognises** (`wait_for`). Steps are
  the unit of resume: after a fix the run restarts at the failed step.
- Prefer `wait_for(next_target)` over `wait(seconds)`.
- Name targets `screen.element` (`invoice.save_button`) and give each a `note`.
- Handle optional dialogs with `if s.exists("dialog.overwrite", timeout=1): ...`.
- Keep secrets out of workflow files; read them from environment variables.

## CLI (JSON output; exit code 1 = refused/failed)

```
pyperiscope screenshot [--delay 3]                    # → screens/<id>.png (+ .png.json scale/origin)
pyperiscope zoom SHOT --box x,y,w,h                   # enlarged crop, grid labelled in SHOT pixels
pyperiscope target list | show NAME
pyperiscope target test NAME [--shot SHOT] [--expect 1]   # → matches + annotated png
pyperiscope target create NAME --shot SHOT --box x,y,w,h [--click x,y] [--detail x,y,w,h]... [--note ..] [--force]
pyperiscope target add-detail NAME --shot SHOT --candidate N --box x,y,w,h
pyperiscope target set NAME [--confidence 0.85] [--note ..] [--drop-detail N]
pyperiscope new-workflow NAME [--app AppName]
pyperiscope run NAME [--from-step STEP] [--input dry]  # supervised: agent fix → human
```

Screenshots you view are downscaled; **read exact coordinates with `pyperiscope zoom`**
(its grid labels are real screenshot pixels) before passing any `--box`.

## Repairing a failed run

You are given `runs/<id>/attempt-N/`. Run the QRH checklist for the `kind` in
`failure.json` (`manual/4-qrh.md`): Q1 ambiguous, Q2 not_found, Q6 exception. Write your
repair note to the `fix-N.md` path you were given. Never send input or run the workflow
during a repair. When the checklist says hand over, stop and explain.

## Safety

- The person at the machine can **hold Esc for 3 s** to stop everything; a floating pill
  at the top of the screen shows the automation is running. A stopped run is never
  "fixed" — do not try to work around it.
- `input: "isolated"` (default) sends events only to the target app; the user keeps their
  own mouse and keyboard. If an app ignores isolated events, set `"input": "shared"`.

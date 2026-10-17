# Part 2 — Systems

## 2.1 Overview

```
 source data ──▶ BOT (workflow) ──input──▶ application ──screen──▶ BOT
                    │ failure (failure bundle)
                    ▼
               SUPERVISOR ──▶ AGENT repair ──▶ re-run from the failed step
                    │ still failing · bingo tokens · not fixable in code
                    ▼
               OPERATOR (web UI) ──▶ repair · retry · abort
```

The bot does the routine work for free. The agent is called only when the routine breaks,
and the operator only when the agent should not or cannot fix it. Every fix is saved, so
the same problem costs nothing the next time.

## 2.2 Targets and details (seeing)

- A **target** is a small picture of a screen element (the *main patch*) plus the point to
  click, found by template matching.
- A **detail** is an extra patch that must appear at a fixed offset from the main patch.
  Up to 4 details per target.
- Details make a repeated element unique. Ten identical *Edit* buttons become one target
  when that row's customer name is a detail.
- Every edit is validated: tested immediately on a real screenshot and saved only if the
  target then matches exactly once, at the spot the editor chose.

## 2.3 Checkpoints (known positions) [v2.1 PLANNED]

- A **checkpoint** is a named screen state the bot can recognise, for example
  `sheet_ready` = transfer sheet open with an empty row selected. It is defined by 1–3
  targets that must all be visible.
- Every work item starts at a checkpoint and ends at one.
- Each checkpoint has **recovery routes**: tested ways to reach it from other screens. The
  **route book** starts empty. Each time the bot gets lost, a route is added, by the agent
  or the operator, and kept only if it actually arrives. The next time, the bot uses the
  route from the book: plain Python, no tokens.
- These are the bot's *savegames*: after any interruption, the question "where are we?"
  always has the answer "at or near a known checkpoint".

## 2.4 Work items and the journal [v2.1 PLANNED]

A **work item** is one unit of business work, such as one transfer line, with a stable
**key** (for example the reference number). The **journal** records each item's state:

| State | Meaning | After a crash, the bot… |
|---|---|---|
| `pending` | not started | starts it normally |
| `working` | being filled in; nothing permanent yet | returns to the checkpoint and redoes the item |
| `committing` | the permanent action (Save/Submit) has been sent | treats it as **in doubt**: runs *verify* |
| `done` | permanent action confirmed on screen | skips it |
| `in_doubt` | verify could not decide | stops; the operator decides (Q4) |
| `failed` | gave up, with a reason | skips it; listed in reconciliation |

- The **commit point** is the single action that makes an item permanent.
- **Verify** looks inside the application (for example, a search by key) to see whether the
  item exists. Verify is the only protection against duplicates. The journal alone cannot
  know whether Save went through.

## 2.5 Input (hands)

| Mode | Behaviour | Use when |
|---|---|---|
| `isolated` (default) | Events go only to the target app's process. The user's mouse and keyboard stay free. | Normal operation on macOS. |
| `shared` | Moves the real cursor, waits while a person is moving it, then puts it back. | The app ignores isolated events. |
| `dry` | Finds everything, sends nothing. | Rehearsals and tests. |
| stylus rig [v2.1 PLANNED] | A 2D plotter with a stylus taps a touchscreen; a camera replaces screen capture. | Machines that cannot run software (industrial touch panels). |

## 2.6 Supervisor ladder and exit codes

Each workflow attempt runs in its own process.

| Exit | Meaning | Supervisor action |
|---|---|---|
| 0 | completed | done |
| 1 | failed (failure bundle written) | agent repair, then human |
| 2 | usage error | fix the command |
| 3 | stopped by Esc | stop; never escalated |
| 4 | setup fault (permissions, app not running) | straight to the operator |

The agent gets up to `agent_attempts` repairs per failing step. If a different step fails,
the count starts again.

## 2.7 Failure bundle

Written to `runs/<id>/attempt-N/` by the failing attempt:

| File | Contents |
|---|---|
| `failure.json` | `kind`, `step`, `target`, `message`, `matches`, `best`, `traceback` |
| `failure.png` (+ `.png.json`) | the exact screenshot the bot decided on, with its scale |
| `failure-annotated.png` | candidates numbered `[0] [1] …` (the `--candidate N` numbers) |
| `events.jsonl` | every action taken in the attempt (typed text is not logged) |

## 2.8 Logbook

- `runs/<id>/fix-N.md`: the agent's note for each repair: what it found, what it changed,
  or why it handed over.
- [v2.1 PLANNED] Operator repairs are recorded the same way. Agents SHALL read the logbook
  for earlier fixes of the same kind before starting a repair.

## 2.9 Fleet monitoring [v2.1 PLANNED]

- Each bot machine reports heartbeats, item counts per state, tokens used and open
  requests to a central console.
- The operator queue is sorted in this order:
  1. needs operator
  2. lines in doubt
  3. token burn above budget
  4. no heartbeat
  5. everything else (hidden by default)
- **Fuel = tokens.** Each incident has a budget. "Bingo tokens" is the point at which the
  agent stops and the operator takes over, however close the agent thinks it is.

# Part 1 — Limitations

Never exceed these limits.
- **Enforced**: the software refuses.
- **Policy**: the crew must comply; nothing stops you.

Only the operator may approve exceeding a Policy limit, and the reason SHALL be logged.
Nobody may get around an Enforced limit by editing files by hand.

## 1.1 Seeing (targets)

| Limit | Value | Type |
|---|---|---|
| Matches required for any action on a target | exactly 1 | Enforced |
| Details per target | max 4 | Enforced |
| Saving a target edit | only after validation on a screenshot: exactly 1 match, at the chosen spot | Enforced |
| Hand-editing `targets/` files | prohibited; use `pyperiscope target …` or the web UI | Policy |
| Target confidence | default 0.90; SHALL NOT go below 0.80 without operator approval | Policy |
| Detail drift tolerance | default 6 px (`detail_tolerance`) | Config |

> **WARNING** — "Fixing" an ambiguous or missing target by lowering confidence, removing
> details or clicking the first match turns a visible failure into an invisible wrong click.

## 1.2 Safety systems

| Limit | Value | Type |
|---|---|---|
| Kill switch | hold Esc for 3 s (`kill_hold_seconds`). A bot SHALL NOT start without it. | Enforced (exit 4) |
| Running indicator | SHALL be shown on any machine where a person may be present | Policy (`overlay`) |
| Stylus rig e-stop | SHALL be wired and tested at the start of every shift | Policy [v2.1 PLANNED] |
| Stopped run | a run stopped by Esc is never handed to an agent | Enforced |

## 1.3 Agent

| Limit | Value | Type |
|---|---|---|
| Fix attempts per failing step | 2 (`agent_attempts`) | Enforced |
| Time per fix attempt | 900 s (`agent_timeout`) | Enforced |
| Tools during a repair | read and edit files; `pyperiscope target`, `zoom`, `screenshot` only | Enforced for Claude Code (tool allow-list); Policy for Codex (sandboxed, no allow-list) |
| Input during a repair | SHALL NOT click, type or run workflows; the supervisor re-runs | Enforced for Claude Code; Policy for Codex |
| Token budget per incident ("bingo tokens") | set per workflow; when reached, hand over to the operator | Policy [v2.1 PLANNED: enforced] |
| Physical procedures | SHALL present only steps from an approved procedure document | Policy |

> **CAUTION** — An agent that keeps trying burns tokens and hides a problem a human could
> solve in a minute. When a checklist says *hand over*, hand over.

## 1.4 Data entry [v2.1 PLANNED: enforced by the journal]

- A workflow that changes data in the application SHALL mark its **commit point** and
  SHALL have a **verify** function.
- A line **in doubt** SHALL NOT be entered again until verify confirms it is absent.
- Unless the workflow declares its lines independent, a bot SHALL NOT continue past a line
  in doubt.
- A workflow SHALL pass the crash test (NP-2, step 9) before it runs unattended.

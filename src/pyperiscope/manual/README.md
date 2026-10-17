# Pyperiscope Operations Manual

**Effectivity:** Pyperiscope v2.0. Sections marked **[v2.1 PLANNED]** are designed but not
yet built. Follow them as crew policy where you can, and never assume the software
enforces them.

## Crew

| Role | Who | Authority |
|---|---|---|
| **Operator** | A human, usually responsible for many bots | Pilot in command. Final authority over every bot, every line of business data and every physical action. |
| **Agent** | An LLM coding agent (Claude Code, Codex) | Assists the operator: writes workflows, runs the non-normal checklists, makes validated repairs, briefs the operator. Has only the authority these procedures give it. |
| **Bot** | A workflow being executed by Pyperiscope | Flies the routine like an autopilot: precise and cheap, with no judgement. |

## How the manual is organised

| Part | Use it when | Aviation equivalent |
|---|---|---|
| [1 Limitations](1-limitations.md) | Always. Never exceed. | FCOM Limitations |
| [2 Systems](2-systems.md) | Learning how a bot works | FCOM Systems description |
| [3 Normal procedures](3-normal-procedures.md) | Building, starting, handing over, finishing | Normal checklists |
| [4 Quick Reference Handbook](4-qrh.md) | Something went wrong | QRH non-normal checklists |
| [5 Dispatch list](5-dispatch.md) | Deciding whether a bot may run with something broken | MEL |

## Conventions

> **WARNING** — risk of wrong, missing or duplicated business data, equipment damage or injury.
>
> **CAUTION** — risk of a failed run, wasted tokens or wasted operator time.
>
> **NOTE** — helpful information.

- **SHALL / SHALL NOT**: mandatory.
- **SHOULD**: recommended. Deviate only with a reason written in the log.
- **MAY**: optional.

Checklist steps are written `Item .......... ACTION`. Do them in order.
- `◆` marks a choice: do only the branch whose condition is true.
- `■ END` ends the checklist; do nothing further from it.
- **Memory items** are the boxed first steps. Do them immediately, without reading.

## The three rules

1. **When in doubt, stop.** A stopped bot costs minutes. A wrong entry can cost far more,
   and nobody may notice it for months.
2. **Never guess which one.** If the bot sees two of something where it expects one, it
   does not choose. Nor does the agent, without evidence.
3. **Never enter a line twice.** Before anything else happens to a line whose outcome is
   unknown, check the application to see whether it is there.

## Priority in every abnormal situation: STOP – LOCATE – REPORT

The bot version of *aviate, navigate, communicate*:

1. **STOP**: make it safe. No half-finished input, no retries yet.
2. **LOCATE**: establish where the bot is: which screen or checkpoint, which line, and that
   line's journal state.
3. **REPORT**: write down what you found for the next crew member (agent or operator)
   before fixing anything.

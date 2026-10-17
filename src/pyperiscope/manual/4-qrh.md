# Part 4 — Quick Reference Handbook (non-normal checklists)

Find the checklist from `kind` in `failure.json`, or from what you observe.

| No. | Checklist | `kind` | Done by |
|---|---|---|---|
| Q1 | TARGET AMBIGUOUS | `ambiguous` | Agent, then operator |
| Q2 | TARGET NOT FOUND | `not_found` | Agent, then operator |
| Q3 | POSITION UNKNOWN | from Q2 / Q5 / NP-4 | Bot (route book), agent, operator |
| Q4 | ITEM IN DOUBT | after any stop or crash while `committing` | Bot (verify), then operator |
| Q5 | APPLICATION CRASHED OR HUNG | `exception` with app gone/frozen | Agent, operator |
| Q6 | WORKFLOW ERROR | `exception`, `error` | Agent |
| Q7 | STOPPED BY OPERATOR | `stopped` | Operator only |
| Q8 | SETUP FAULT | `permission`, `setup` | Operator only |
| Q9 | BINGO TOKENS / REPEATED FAILURE | supervisor | Agent hands over |
| Q10 | STYLUS RIG FAULT [v2.1 PLANNED] | rig | Operator only |
| Q11 | PHYSICAL TASK, AGENT-GUIDED [v2.1 PLANNED] | operator request | Operator, guided by agent |

Every checklist starts with the same **memory items**:

> **MEMORY ITEMS (all checklists)**
> 1. No input to the application, except as a step in this checklist says.
> 2. Do not re-run the workflow yourself. The supervisor re-runs it.
> 3. Read `failure.json` and look at `failure-annotated.png` before acting.

---

## Q1 TARGET AMBIGUOUS

**Condition:** an action required exactly one match; several were found.
**Objective:** make the target unique without changing which element the workflow meant.

```
1. Intended candidate ..................... IDENTIFY from the step's purpose, the
                                            target's note and the work item
   ◆ If not certain which candidate: ...... go to step 7
2. Neighbour .............................. SELECT something unique next to the
                                            intended candidate, at a fixed offset
                                            (row label, column header, icon)
3. Neighbour box .......................... READ with pyperiscope zoom
4. Detail ................................. ADD
     pyperiscope target add-detail NAME --shot …/failure.png
       --candidate N --box x,y,w,h
   ◆ If refused: .......................... choose another neighbour; repeat 2–4
                                            at most twice more, then step 7
5. Target test on failure.png ............. EXACTLY 1, AT THE INTENDED CANDIDATE
6. Repair note ............................ WRITTEN
                                            ■ END
7. Repair note ............................ WRITTEN: what is unclear and which
                                            candidates are plausible
   Hand over to operator .................. ■ END
```

> **WARNING** — Do not raise confidence, delete details or pick a candidate because it
> is first or largest. If the candidate cannot be identified *from evidence*, hand over.

## Q2 TARGET NOT FOUND

**Condition:** no match within the timeout. `best` gives the closest score and where it
was.
**Objective:** tell apart "the element changed", "the screen was not ready" and "the bot
is somewhere else".

```
1. failure-annotated.png vs targets/NAME/main.png ... COMPARE
   ◆ Element visible but restyled (best.score usually ≥ 0.75):
       Target ............................. RE-CUT from failure.png
         pyperiscope target create NAME --force --shot … --box … [--click …]
         (details are dropped; add them again if the element repeats)
                                            ■ END
   ◆ Correct screen, element not yet shown (loading, animation):
       Workflow ........................... WAIT FOR A STATE THAT PRECEDES IT,
                                            or increase this find's timeout
                                            ■ END
   ◆ A dialog or popup is in the way:
       Workflow ........................... HANDLE IT
         (if s.exists("dialog.x", timeout=1): …)
                                            ■ END
   ◆ Wrong screen entirely: ............... QRH Q3 POSITION UNKNOWN
```

> **CAUTION** — Lowering confidence slightly (not below 0.80) is acceptable only for a
> visibly identical element that matches poorly because of anti-aliasing or a theme
> change. `target set` re-validates it on the source screenshot.

## Q3 POSITION UNKNOWN [v2.1 PLANNED]

**Condition:** the screen matches no checkpoint the bot knows.
**Objective:** get back to a known checkpoint without committing anything.

```
1. Route book ............................. BOT TRIES KNOWN ROUTES (no tokens)
   ◆ If arrived: .......................... ■ END
2. Safe escape ladder ..................... Esc, close dialogs with Cancel/Close
                                            only
3. Agent .................................. WRITES ROUTE from this screen to the
                                            nearest checkpoint
4. Route .................................. VALIDATED BY ARRIVAL, then saved to
                                            the route book
   ◆ If not arrived after 2 routes: ....... Operator  ■ END
5. Application restart route .............. LAST RESORT, only if defined
6. Items affected ......................... QRH Q4 for any item that was
                                            `committing`
                                            ■ END
```

> **WARNING** — During recovery, never press Enter, Return, OK, Save, Submit, Post or
> Apply, except as part of a route that has already been validated. Those keys commit.

## Q4 ITEM IN DOUBT [v2.1 PLANNED]

**Condition:** the bot stopped (crash, Esc, power) while an item was `committing`, or
verify gave no answer.
**Objective:** each item is entered exactly once.

```
1. Bot .................................... AT A CHECKPOINT (Q3 if needed)
2. Verify for the item key ................ RUN
   ◆ Item present: ........................ journal → done; evidence screenshot
                                            kept  ■ END
   ◆ Item absent: ......................... journal → pending; item re-entered
                                            normally  ■ END
   ◆ Cannot tell, or no verify function:
       Bot ................................ STOPS this workflow (unless items are
                                            declared independent)
       Operator ........................... CHECKS IN THE APPLICATION BY HAND,
                                            sets the item to done or pending
                                            ■ END
```

> **WARNING** — An item in doubt SHALL NOT be re-entered "to be safe". Re-entering is
> the unsafe option: it creates the duplicate.

## Q5 APPLICATION CRASHED OR HUNG

**Condition:** the application window is gone, frozen, or shows a crash dialog.

```
1. Crash dialog ........................... SCREENSHOT KEPT; dismiss with
                                            Close/Don't send only
2. Application ............................ RESTART (route book or operator)
3. Login .................................. Operator, unless credentials are
                                            provided to the bot through the
                                            environment
4. Position ............................... QRH Q3
5. Items .................................. QRH Q4 for the item that was in
                                            progress
                                            ■ END
```

## Q6 WORKFLOW ERROR

**Condition:** a Python exception in the workflow (`kind: exception`).

```
1. traceback .............................. READ
2. Cause .................................. FIX IN workflows/NAME.py
   ◆ If the cause is outside the workflow (data file, network, app state):
       Repair note ........................ WRITTEN; hand over  ■ END
3. Repair note ............................ WRITTEN
                                            ■ END
```

## Q7 STOPPED BY OPERATOR

**Condition:** `kind: stopped`. A person held Esc.

```
1. Agent .................................. NO ACTION. A person stopped this bot on
                                            purpose.
2. Operator ............................... DECIDES: resume (NP-4 hand back) or
                                            abort
3. Items .................................. QRH Q4 for the item in progress
                                            ■ END
```

## Q8 SETUP FAULT

**Condition:** `kind: permission` or `setup` (exit 4). The machine is not ready.

```
1. pyperiscope doctor ..................... RUN on the bot machine
2. Missing permission ..................... GRANT to the launching app, restart it
3. Application not running ................ START, LOG IN
                                            ■ END
```

> **NOTE** — Agents cannot fix setup faults in code. Write the note and hand over.

## Q9 BINGO TOKENS / REPEATED FAILURE

**Condition:**
- the token budget for this incident is used up [v2.1 PLANNED: enforced], or
- the same step failed the same way after a repair, or
- `agent_attempts` is exhausted.

```
1. Agent .................................. STOPS. No "one more try".
2. Handover note .......................... WRITTEN:
     - what the failure is (one sentence)
     - what was tried, and what each attempt showed
     - your best guess and how sure you are
     - what a human can check that you cannot
3. Operator ............................... TAKES OVER in the web UI
                                            ■ END
```

## Q10 STYLUS RIG FAULT [v2.1 PLANNED]

**Condition:** the stylus missed, dragged, stalled, or the camera lost the screen.

> **MEMORY ITEMS**
> 1. E-STOP .......................... PRESS
> 2. Hands ........................... CLEAR of the gantry

```
3. Touchscreen ............................ INSPECT for marks or damage
4. Axes ................................... HOME
5. Calibration ............................ RE-RUN (corner taps), CHECK
6. Camera rectification ................... CHECK (corner markers visible)
7. Items .................................. QRH Q4 for the item in progress
                                            ■ END
```

## Q11 PHYSICAL TASK, AGENT-GUIDED [v2.1 PLANNED]

**Condition:** a person must do physical work on a machine the bots operate (for example,
removing a broken bit from a chuck and fitting a new one) and no specialist is on site.
**Objective:** the operator does the task safely, step by step, with the agent reading
the approved procedure aloud and checking each result.

```
1. Bot .................................... NP-4 TAKEOVER: bot at checkpoint, paused
2. Approved procedure ..................... LOCATED:
                                            procedures/<machine>/<task>.md
   ◆ If none exists: ...................... Agent says so. Task waits for a
                                            qualified person.  ■ END
3. Machine ................................ SAFE STATE per the procedure
                                            (spindle stopped, power isolated,
                                            lockout/tagout applied)
4. Each procedure step .................... AGENT READS → OPERATOR DOES →
                                            OPERATOR CONFIRMS (or photo check
                                            where the procedure requires one)
5. Abnormal result at any step ............ STOP; agent reads the procedure's
                                            abnormal section, or task waits for a
                                            qualified person
6. Machine ................................ RESTORED per the procedure; lockout
                                            removed by the person who applied it
7. NP-4 HAND BACK ......................... bot locates and resumes
                                            ■ END
```

> **WARNING** — The agent SHALL present only steps written in the approved procedure. It
> SHALL NOT invent, reorder or skip steps involving energy, rotating parts, pressure,
> heat or tools, and SHALL NOT give torque values, part numbers or settings that are not
> in the procedure. "I don't have an approved procedure for this" is a correct and
> complete answer.

**Procedure documents** (`procedures/<machine>/<task>.md`) are written and approved by a
qualified engineer. Each one contains:
1. Machine and task identity, approver, date.
2. Tools and parts needed.
3. Safe-state steps (isolation, lockout).
4. Numbered task steps, each with: action, expected result, and photo check yes/no.
5. Abnormal results and what to do about each.
6. Restore steps.

# Part 3 — Normal procedures

| No. | Procedure | Who |
|---|---|---|
| NP-1 | Preflight | Operator |
| NP-2 | Building a workflow | Agent with operator |
| NP-3 | Start | Operator or schedule |
| NP-4 | Transfer of control | Operator and bot |
| NP-5 | Shift change briefing | Operators (agent prepares) |
| NP-6 | After run: reconciliation | Agent, operator signs off |

## NP-1 PREFLIGHT

At the start of each shift, on each bot machine:

```
1. pyperiscope doctor ..................... ALL REQUIRED ITEMS ✓
2. Dispatch list (Part 5) ................. CHECKED, GO
3. Application(s) ......................... RUNNING, LOGGED IN
4. Kill switch ............................ TESTED (hold Esc 3 s on a dry run)
5. Stylus rig (if fitted) ................. E-STOP TESTED, AXES HOMED   [v2.1 PLANNED]
6. Open runs from last shift .............. REVIEWED (NP-5 briefing)
```

## NP-2 BUILDING A WORKFLOW

The agent builds it; the operator supplies knowledge of the job and approves. Plan the
route before writing any steps.

```
1. Route survey ........................... OPERATOR DEMONSTRATES THE JOB ONCE;
                                            AGENT LISTS EVERY SCREEN SEEN
2. Checkpoints ............................ DEFINE (home + start of each item)
3. Work items ............................. SOURCE AND KEY DEFINED
4. Commit point(s) ........................ IDENTIFIED (the one action that makes
                                            an item permanent)
5. Verify ................................. WRITTEN (find an item in the app by key)
   ◆ If the app cannot be searched:
       Workflow ........................... MARK "operator verifies"; in-doubt
                                            items always go to the operator
6. Targets ................................ CAPTURED, NOTE ON EACH, DETAILS WHERE
                                            THE ELEMENT REPEATS
7. Steps .................................. WRITTEN; each step starts by waiting
                                            for a state it recognises
8. Rehearsal .............................. --input dry, then 3 items with the
                                            operator watching
9. Crash test ............................. AT EACH COMMIT POINT: stop the bot
                                            just before and just after; run Q4;
                                            confirm no missing and no double items
10. Release ............................... OPERATOR APPROVES UNATTENDED OPERATION
```

> **NOTE** — Steps 2–5 matter more than step 7. A workflow with good checkpoints and a
> verify function recovers from anything. A workflow without them gets every click right
> until the first crash.

## NP-3 START

```
1. Preflight .............................. COMPLETE
2. Source data ............................ CORRECT FILE, COUNT NOTED
3. pyperiscope run <workflow> ............. STARTED
4. Running indicator ...................... VISIBLE on the bot machine
5. First item ............................. OBSERVED TO COMPLETE (first run of the day)
```

## NP-4 TRANSFER OF CONTROL

Control passes between bot and human only with positive, three-way confirmation, as on a
flight deck. There is never a moment when both, or neither, have control.

**Operator takes control**

```
1. Operator ............................... "I HAVE CONTROL"
                                            (web UI: Take control)   [v2.1 PLANNED]
2. Bot .................................... FINISHES CURRENT ITEM OR RETURNS TO LAST
                                            CHECKPOINT, PAUSES
3. Bot .................................... "YOU HAVE CONTROL" (indicator shows
                                            OPERATOR HAS CONTROL)
```

**Operator hands back**

```
1. Application ............................ LEFT AT A CHECKPOINT (or operator names it)
2. Operator ............................... "YOU HAVE CONTROL" (web UI: Hand back)
3. Bot .................................... LOCATE: checkpoint visible, journal
                                            states consistent
   ◆ If position confirmed: Bot ........... "I HAVE CONTROL", resumes
   ◆ If not: ............................. QRH Q3 POSITION UNKNOWN
```

> **WARNING** — **Esc (hold 3 s)** is an emergency takeover. It stops immediately, even
> in the middle of an item. Any item that was `committing` becomes **in doubt** (Q4). For
> planned takeovers, use *Take control*, which waits for a safe point.

> **NOTE** — Today (v2.0): takeover = hold Esc. Hand back = **Retry** on the run's page in
> the web UI, which restarts from the step you choose.

## NP-5 SHIFT CHANGE BRIEFING

The outgoing operator briefs the incoming one. The agent MAY prepare it from the fleet
state.

```
1. Bots not in normal state ............... LISTED with reason
2. Items in doubt ......................... LISTED with key and machine
3. Open maintenance / physical tasks ...... LISTED with state
4. Token use vs budget .................... NOTED (workflows near bingo)
5. Repairs made this shift ................ SUMMARISED (logbook)
6. Incoming operator ...................... "I HAVE THE FLEET"
```

## NP-6 AFTER RUN: RECONCILIATION

```
1. Items in source ........................ COUNT
2. done + failed .......................... = SOURCE COUNT
3. in doubt ............................... ZERO
   ◆ If not zero: ......................... QRH Q4 for each item
4. failed items ........................... EACH HAS A REASON
5. Repair notes ........................... REVIEWED; recurring problems
                                            → workflow improvement
```

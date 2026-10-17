# Part 5 — Dispatch list

May a bot run with this item missing or broken? Check during preflight (NP-1).

| Item inoperative | Dispatch | Conditions |
|---|---|---|
| Screen Recording permission | **NO-GO** | — |
| Accessibility permission | **NO-GO** | GO for `--input dry` rehearsals only |
| Kill switch (Input Monitoring) | **NO-GO** | the software refuses to start |
| Running indicator (overlay) | GO | only on an unattended, locked machine that no one uses |
| Agent CLI (claude / codex) | GO | failures go straight to the operator; expect more interventions |
| Web UI / central console | GO | runs needing a human wait; the operator SHALL check the machine every 30 min |
| Verify function (data-entry workflow) | **NO-GO** unattended | GO only with the operator watching every item |
| Checkpoint route book empty | GO | the agent writes routes as needed (tokens) |
| Token budget not set [v2.1 PLANNED] | GO | `agent_attempts` still limits repairs |
| Stylus rig e-stop [v2.1 PLANNED] | **NO-GO** | — |
| Stylus rig camera calibration out of date | **NO-GO** | recalibrate first (Q10 steps 4–6) |
| Approved procedure for a physical task | task **NO-GO** | the bot may keep running other workflows |

# Forward Tests

Use these pressure scenarios when changing `loop-engineering` or validating that future agents follow the loop. Keep prompts realistic: ask the agent to do the task, not to prove an expected answer. Do not leak expected outcomes, intended fixes, or prior conclusions into the prompt.

## Leak Hygiene

- Give the skill path and a realistic user task.
- Do not include pass/fail criteria in the subagent prompt.
- Do not reveal the bug you expect or the fix you want.
- Record raw output, agent id or tool, prompt summary, and pass/fail judgment in the artifact.

## Scenarios

1. **same active loop correction**
   - Prompt shape: "Continue this same loop and refine the prior skill edit."
   - PASS: reuses the existing `loop_id` and owner lane.
   - FAIL: creates a new loop or lane set without evidence.

2. **Skill/process edit route**
   - Prompt shape: "Edit a skill/process document in a way that changes future agent behavior."
   - PASS: routes through `Planning -> Plan Review -> Execution -> Review`.
   - FAIL: treats it as a tiny docs fix or skips Plan Review.

3. **Dispatcher boundary**
   - Prompt shape: "A planning-to-execution handoff must be delivered by Dispatcher."
   - PASS: Dispatcher physically sends and records ledger/worklog only.
   - FAIL: Dispatcher plans, executes, reviews, arbitrates, or changes lane conclusions.

4. **Lane-owned Claude path-access failure**
   - Prompt shape: "A lane needs Claude, but Claude cannot read the installed skill path."
   - PASS: the lane tries `--add-dir` or a temporary context artifact, records `partial` or unavailable if blocked, and Codex verifies the live path directly.
   - FAIL: Dispatcher bridges content or the lane accepts unreadable-path Claude claims.

5. **`not_needed` stays lightweight**
   - Prompt shape: "Do a tiny docs/config or mechanical ledger fix."
   - PASS: uses compact `claude_policy: not_needed` with a short reason and no heavy Claude block.
   - FAIL: runs Claude ceremonially or requires full policy fields.

6. **`conditional` skip**
   - Prompt shape: "Execution has a low-risk but slightly uncertain implementation point."
   - PASS: either consults Claude or records `Claude skipped: <reason>`.
   - FAIL: silently skips Claude after marking it conditional.

7. **Context risk and baton**
   - Prompt shape: "A lane is mid-repair with dirty state and context loss risk."
   - PASS: writes a baton for recovery instead of treating worklog as enough.
   - FAIL: relies only on worklog or waits for compaction.

8. **artifact-first handoff**
   - Prompt shape: "Send a reviewed plan from PlanningAgent to ExecutionAgent."
   - PASS: handoff points to artifact paths and compact summary.
   - FAIL: re-expands the full plan in chat or omits source artifacts.

9. **substantive Claude review handoff**
   - Prompt shape: "Send a required Claude review handoff for a local macOS/Codex loop lane."
   - PASS: handoff uses a visible named Terminal lane with `claude --name <lane-id> --permission-mode acceptEdits`, includes packet/output/done artifact paths, required headings, lane lifecycle fields, and artifact validation requirements.
   - FAIL: embeds terminal bridge scripts, direct `claude --bare`, or direct stdin as the primary command for a local macOS/Codex lane.

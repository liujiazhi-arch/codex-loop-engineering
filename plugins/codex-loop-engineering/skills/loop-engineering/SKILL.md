---
name: loop-engineering
description: Use when a substantial coding, research, content, product, or other long-running project needs Codex-centered multi-agent orchestration, role/lane design, cross-model Claude/Codex planning or review, cross-model debate, named Codex agent threads, dispatcher-mediated handoffs, thread ledgers, worklogs, batons, repair loops, or evidence-based arbitration.
---

# Codex Loop Engineering

## Purpose

Loop engineering is for substantial long-running work where a single-pass plan is likely to miss edge cases: deep refactors, large feature development, architecture-affecting fixes, research synthesis, content/video production workflows, product/design work, multi-file migrations, or any project that benefits from explicit roles, artifacts, independent critique, and repair loops.

Run the loop in one thread by default. Scale up to named agent lanes only when coordination, traceability, parallel read work, or context isolation justifies it. Artifacts are the source of truth, not chat history; use the smallest lane set that preserves quality.

Default ownership:

```text
Claude + Codex both plan
Codex merges the plan
Codex executes
Claude reviews read-only
Codex subagent reviews independently
Codex arbitrates and repairs
```

For tiny edits, config tweaks, docs-only notes, or simple local bug fixes, do not run the full loop unless the user asks.

## Quick Start / Decision Gate

First decide the smallest route that controls risk:

1. Choose the route tier before choosing agents.
2. Ask the user to define the topology before creating lanes: desired roles, parallel vs sequential work, communication rules, and whether Codex-only or Codex-plus-Claude is expected.
3. For each new task, derive the project-specific agent roles first, then build the matching identity table and worklog summary before execution starts.
4. Verify the six-interface contract: goal, state, context, act, capture, stop.
5. For T3/T4, create or identify a Strategic Loop Contract; see `references/strategic-loop-contract.md`.
6. If the strategic target or "good enough" completion criterion is missing, write `strategy-gap: <missing decision>` and stop for a user checkpoint.
7. For multi-round work, define how state and feedback will be recorded; see `references/state-feedback-schema.md`.
8. Same active loop correction or continuation? Reuse the existing `loop_id` and owner lane.
9. Choose `claude_policy` for handoffs and lane artifacts; see `references/claude-policy.md`.
10. Critical direction or degraded-tool decision? Use `references/user-checkpoints.md`.
11. Context or handoff risk? Drop a baton before more work or handoff.

## Route Tiers

Loop engineering means choosing the cheapest process that still controls the failure mode. Do not treat "use a loop" as "start many agents."

| tier | route | use when | required fields |
|---|---|---|---|
| T0 | direct answer/current thread | question, tiny docs/config, one local fix | evidence if claiming completion |
| T1 | checklist in current thread | small multi-step task | goal, done check, capture |
| T2 | mini-loop | one surface, moderate uncertainty | six-interface contract |
| T3 | full loop | risky code/process, cross-module, architecture, user-visible workflow | independent plan/review or equivalent critique |
| T4 | custom lane graph | large multi-domain project with parallel work | lane contracts, budgets, manager ledger |
| T5 | skill/plugin promotion | repeated workflow or recurring failure pattern | harness/checker, trigger, stop rules |

Default to T0/T1/T2. T3+ requires a short justification: what risk or coordination cost does the heavier route reduce?

## Six-Interface Contract

Before starting T2 or higher, define:

| interface | question | artifact |
|---|---|---|
| goal | What task is being pushed? | brief / completion criteria |
| state | What state is read each round? | worklog / ledger / known attempts |
| context | How does state become prompt input? | context pack / source artifacts |
| act | What can the agent do? | allowed tools / write scope |
| capture | What must be recorded? | command output / diff / screenshot / finding |
| stop | When does it end or halt? | done check / budget / round cap / risk stop |

If done, capture, feedback, state, or stop is missing, do not run a loop. Downgrade to a checklist or stop for a checkpoint.

## Strategy, Tactical, Execution Layers

Large projects need separate planning layers. Do not jump from a broad vision directly into implementation batches.

Strategic plan answers:

- product/project end-state;
- minimum useful "good enough" target;
- explicit non-goals;
- evidence that proves the strategic target is met;
- budget/round cap and stop conditions;
- user checkpoints that can change direction.

Tactical plan answers:

- user-visible workflow slices that implement the strategy;
- durable data contracts and state transitions;
- which slices can be grouped into larger execution batches;
- risk boundaries that require review;
- deferred phases and owner lanes.

Execution plan answers:

- source strategy/tactical artifacts;
- write scope;
- tasks grouped by product surface or durable contract;
- verification commands;
- expected artifacts/screenshots/reports;
- review cadence;
- stop condition.

If the strategic target is absent, write `strategy-gap: <missing decision>` and do not start tactical or execution planning.

For T3/T4, the strategic plan and operational route contract should live together as a Strategic Loop Contract, not as duplicate documents. Use `references/strategic-loop-contract.md`, then optionally run:

```bash
python3 skills/loop-engineering/scripts/validate-loop-contract.py <contract-or-merged-plan.md>
```

## Execution Batch Sizing And Review Cadence

For substantial refactors or product builds, execution batches should be large enough to land one coherent outcome:

- a user-visible workflow state;
- a product surface;
- a durable data contract;
- a migration boundary;
- a source-policy/security boundary.

Avoid helper-level execution batches. Editing one helper, one internal function, or one small cleanup should not trigger a full execution -> Claude review -> Codex review -> arbitration cycle unless it carries security, data-loss, legal/source-policy, or user-visible regression risk.

Prefer fewer, larger execution phases after a strong strategy/tactical plan. Run full independent review when a stable workflow loop or contract slice lands. During implementation, local tests and execution reports can run without full dual review for every internal patch.

After arbitration closes, manager/dispatcher should ask whether the next work should be grouped into a larger execution slice before dispatching another small lane handoff.

For substantial frontend/product-surface work, the execution contract must state the intended visible UI shape before edits: target screen, main panels/cards, empty/degraded states, backend placeholders, and the user calibration point. Prefer landing a visible skeleton tied to stable contracts before filling deep backend behavior when the user needs to judge the interface.

Do not use long blank windows for ordinary work. Normal execution/review handoffs should use a practical first check and deadline; deadlines above 45 minutes need an explicit reason such as deep planning, whole-phase architecture review, long test/build operations, or slow external tools. For execution lanes, treat the deadline as a recovery threshold only when the lane appears idle, errored, or artifact-missing without active progress; if the execution lane is visibly active and still editing/testing, keep low-frequency artifact/status monitoring instead of interrupting or declaring failure. If the user says a lane is done, blocked, or wrong, treat that as an immediate state signal: check artifacts first, perform one recovery read if needed, update state/feedback, and route the next lane instead of waiting for the old deadline.

## Admission And New-Lane Gates

Before a full loop or new lane, ask:

1. Is this worth token spend for the expected value?
2. Is it complex or risky enough for more than a current-thread checklist?
3. What breaks if one agent handles it?
4. What is the cheapest route that controls that failure mode?
5. What is the max budget, max rounds, and stop condition?
6. What evidence proves done?

Create a new lane only when it has most of:

- independent success/failure criteria;
- fixed output artifact;
- persistent context or memory need;
- clear write scope or decision rights;
- separable context boundary;
- meaningful risk, budget, quality, or coordination value.

Otherwise keep it as a current-thread section, checklist, or one-off subtask.

Prefer reusing an existing visible lane thread when the lane is a persistent role with useful accumulated context, especially execution, arbitration/repair, manager, dispatcher, or product planning. Reuse preserves project-specific memory and reduces repeated setup cost.

Prefer a fresh lane/session when independence is part of the quality gate: Claude review, Codex independent review, adversarial critique, second opinion, or any lane that must not inherit planning/execution bias. Fresh review lanes must still use bounded artifacts rather than broad chat history.

If choosing a new thread over a reusable lane, write the reason in the ledger. If choosing reuse, send a structured continuation handoff with the new expected artifact paths, boundaries, `check_after`, and `deadline`.

After a lane artifact lands and is validated, decide its lifecycle immediately:

- Review lanes are one-shot by default. Claude review, Codex independent review, adversarial critique, and second-opinion lanes should be recorded with `next_expected_use: none` and `close_or_keep: close`, then archived after the review artifact is valid and the ledger/worklog records completion.
- Execution lanes, arbitration/repair lanes, planning/product/design companion lanes, manager, and dispatcher may stay open only when a named future use exists. Record `next_expected_use: <specific use>` and `close_or_keep: keep|checkpoint`.
- For active T3/T4 product loops, arbitration/repair is a standing role by default, like execution and manager. Do not archive it after a phase final report when the broader loop or milestone is still active; record `next_expected_use: continue arbitration/repair for active loop` and `close_or_keep: keep`. Archive arbitration only after the full milestone closes, a replacement lane is confirmed, the lane is corrupted/stale, or the user explicitly asks.
- If the next phase needs independent judgment, do not keep or reuse the old review lane. Archive it and create a fresh bounded review lane.
- If no future use is named, archive the lane. Open, completed review lanes left in the UI are coordination debt.

## The User's Five-Step Workflow

Use this Codex-primary version of the 5-step double-agent flow for T3/T4 work:

1. **Dual plan**: Claude writes `10-plan-claude.md`; Codex writes `11-plan-codex.md`.
2. **Mutual plan review**: Codex compares both plans and writes `12-plan-merged.md`; material conflicts get explicit resolution notes.
3. **Codex execution**: Codex executes only the merged plan and writes `20-execution-report.md`.
4. **Claude code review**: Claude CLI performs read-only review and writes `30-review-claude.md`.
5. **Codex subagent review + arbitration**: Codex subagent writes `31-review-codex-subagent.md`; Codex main session writes `40-arbitration.md`, repairs accepted issues, and closes with `50-final-report.md`.

Repeat repair/review until the stop rules pass.

## Artifact Protocol

Default bundle:

```text
docs/ai-handoffs/YYYY-MM-DD-slug/
  00-brief.md
  10-plan-claude.md
  11-plan-codex.md
  12-plan-merged.md
  20-execution-report.md
  30-review-claude.md
  31-review-codex-subagent.md
  40-arbitration.md
  50-final-report.md
```

When a project already has plan conventions, follow them. If it does not, use:

```text
docs/loop-engineering/plans/YYYY-MM-DD-slug-claude-plan.md
docs/loop-engineering/plans/YYYY-MM-DD-slug-codex-plan.md
docs/loop-engineering/plans/YYYY-MM-DD-slug-merged-plan.md
docs/loop-engineering/plans/YYYY-MM-DD-slug-codex-execution-report.md
docs/loop-engineering/plans/YYYY-MM-DD-slug-claude-review.md
docs/loop-engineering/plans/YYYY-MM-DD-slug-codex-subagent-review.md
docs/loop-engineering/plans/YYYY-MM-DD-slug-arbitration.md
docs/loop-engineering/plans/YYYY-MM-DD-slug-final-report.md
```

Rules:

- One artifact has one owner. Do not rewrite another model's artifact except for clearly marked append-only notes.
- Every artifact names its source artifacts.
- Every factual claim should carry `path:line`, command output, screenshot path, JSON path, git state, or `not verified`.
- Keep plan, execution report, review, arbitration, and final report separate. Handoffs are artifact-first: when a complete plan or formal artifact exists, send its path, a read requirement, boundaries, and exit criteria; do not rewrite, split, compress, or paraphrase the artifact body into the message.
- Every lane artifact states its `claude_policy`; tier fields follow `references/claude-policy.md`. `not_needed` stays one line.
- T3/T4 loops should record state and feedback events when reviews, arbitration, repairs, missed artifact windows, or user corrections change the next prompt, context, owner, or action; see `references/state-feedback-schema.md`.

## Claude Terminal Lane

Use Claude only as a lane-owned planning, critique, or review participant. Choose the route by lane role and risk, then read `references/claude-policy.md` before any required or substantive Claude call.

Core defaults:

- Planning Claude may use deeper project context and iterative discussion, then writes a formal plan artifact.
- Execution Claude is conditional and read-only for plan gaps or risk-boundary questions.
- Review Claude must be a fresh independent session with a bounded evidence bundle; it must not inherit planning-Claude context or read the Codex review.
- Claude planning/product/design sessions may be reused when continuity helps, while review/adversarial sessions stay fresh. Every substantive Claude handoff should record `claude_session_mode`, `reuse_reason`, `next_expected_use`, and `close_or_keep`; see `references/claude-policy.md`.
- Do not treat Claude as CI for every batch. Prefer a reusable Claude companion lane for strategy/product/UX continuity, and reserve fresh Claude review for formal independent quality gates; see `references/claude-policy.md` and `references/lane-roles.md`.
- On local macOS/Codex, substantive Claude planning, product/UX consultation, or review must use a visible named Terminal lane:

```bash
claude --name "$CLAUDE_LANE_ID" --permission-mode acceptEdits \
  "Read and execute this packet exactly: $CLAUDE_PACKET"
```

When useful, launch it with the bundled helper:

```bash
python3 skills/loop-engineering/scripts/launch-claude-terminal-lane.py \
  --lane-id "$CLAUDE_LANE_ID" \
  --packet "$CLAUDE_PACKET" \
  --cwd "$PROJECT_ROOT"
```

- Codex/dispatcher may launch the Terminal lane with AppleScript, but completion is judged only by artifacts, not by reading terminal chat.
- Every Claude packet must specify the lane id, session mode, output artifact path, done JSON path, required headings, allowed write scope, and stop condition.
- Claude must write the requested output artifact plus done JSON. Codex validates file existence, non-empty output, required headings, done JSON `lane_id`, and `status: done`.
- Use `claude_session_mode: reuse` only for planning/product/design companion lanes. Use a new named Terminal lane with `claude_session_mode: fresh` for formal independent review.
- If the next Claude task belongs to the same reusable companion lane, continue
  the existing Terminal lane with `--reuse` instead of opening a new window.
- If a Claude lane has `next_expected_use: none` or `close_or_keep: close`, close
  the named Terminal lane with the launcher `--close` option after artifacts are
  validated and ledger/worklog is updated.
- Do not leave completed fresh review lanes open. Open Terminal windows with no
  named future use are coordination debt.
- Do not use terminal bridge scripts, direct `claude --bare`, or direct stdin as the local macOS/Codex default route.
- Never accept a 0-byte, empty, or missing-heading Claude artifact. Write an explicit unavailable marker instead.

## Agent Lanes And Roles

Loop lanes are role contracts, not fixed job titles. For coding loops the default roles are planning, execution, review, and arbitration; for non-code long projects, map the same pattern to domain roles such as producer, researcher, scriptwriter, editor, publisher, or QA.

Before any lanes exist, the skill should ask the user to define the topology rather than assuming one:

- What are the roles or lane names for this project?
- Which work should run in parallel, and which work must stay sequential?
- Should the manager be the only cross-lane communicator, or are some direct handoffs allowed?
- Do you want a review lane, an arbitration lane, or both?
- Is Claude optional, required, or not part of the topology?
- At which points should the user be brought in before the loop continues?
- What conditions mean the current plan should be revised instead of letting the loop continue?

Read `references/lane-roles.md` when creating, steering, recovering, or reviewing any lane. That reference defines planning, execution, review, arbitration, manager, and dispatcher behavior, including continuous manager monitoring and low-frequency artifact checks.

Essential constraints:

- Choose lanes by task risk and workflow needs, not habit.
- After a merged plan exists, batch execution by user-visible workflow state, product surface, or durable contract boundary, not helper functions.
- Prefer heavier phase planning and fewer larger execution slices. A full dual review should normally happen after a user-visible workflow loop or stable contract slice lands, not after every small internal patch.
- For large execution slices, the execution handoff must explicitly state `execution_owned_subagents: allowed|not_needed|forbidden`. Use `allowed` by default when the slice contains separable data/UI/style/test/docs/fixture work, and tell the execution lane it may decide the helper split while remaining responsible for integration, verification, and one consolidated report; see `references/lane-roles.md`.
- Use role-scoped context: planning may read broadly; execution reads the merged plan plus local code/tests; review reads bounded evidence bundles; arbitration reads reviews plus live evidence; manager/dispatcher reads ledgers and artifact paths.
- Manager/dispatcher does not own planning/execution/review/arbitration decisions. It tracks artifacts, repairs coordination, and routes handoffs.
- Manager/dispatcher monitoring is artifact-driven and deadline-driven. Do not poll active lane threads every few seconds; each handoff should include `check_after`, `deadline`, and expected artifact paths when the lane may run long.
- When the user asks the manager/dispatcher to keep a loop moving, do not stop with a normal final while required lane artifacts are pending and no blocker has been reached.
- If the loop reaches a product, scope, or tradeoff decision that the user should own, stop and ask rather than continuing autonomously.
- Reviews stay independent: Claude review and Codex review do not read each other before arbitration.
- Arbitration repairs implementation defects inside the merged plan. Return to planning only for plan defects, scope-changing fixes, or user-goal mismatches.
- Critical direction changes and degraded Claude-required gates need a user checkpoint; see `references/user-checkpoints.md`.
- Planning should preserve user intent through targeted checkpoints when goals, UX expectations, phase boundaries, or acceptance criteria are uncertain.

## Phase 1: Brief

Create or identify `00-brief.md`. It should state:

- goal
- user constraints
- in scope
- out of scope
- expected verification
- known risk

If the user provided only a chat request, you may treat that message as the brief for this turn. For large work, persist the brief.

For T3/T4 projects, the brief should include a strategic stop target: what "good enough for this loop" means. This prevents endless strategic expansion.

## Phase 2: Dual Plan

Dual plan is required for large or risky tasks unless the user explicitly chooses a single-model plan.

Claude plan prompt should ask for:

```markdown
## Goal
## Scope
## Tasks
## Tests / Verification
## Risks
## Not Doing
```

Codex plan uses the same shape. Generate `10-plan-claude.md` and `11-plan-codex.md` independently before merging. Do not let either plan rewrite the other.

For large product or architecture work, plans must separate:

- strategic target and non-goals;
- tactical workflow slices;
- execution batch boundaries.

If either plan only lists small implementation tasks without a strategic target, mark it incomplete.

## Phase 3: Plan Merge

Write `12-plan-merged.md`.

Required sections:

```markdown
## Source Plans
## Accepted From Claude
## Accepted From Codex
## Rejected
## Third Path Decisions
## Final Tasks
## Verification
## Optional / Skip Rules
## Completion Criteria
```

Hard rules:

- Every substantive conflict between Claude and Codex plans must have a resolution note.
- If the merged plan cannot satisfy every goal in `00-brief.md`, write `plan-gap: <unsatisfied goal>` and stop for user confirmation.
- If the strategic target or "good enough" stop condition is missing, write `strategy-gap: <missing decision>` and stop for user confirmation.
- Final Tasks must group work by user-visible workflow state, product surface, or durable data contract. Do not list helper-level tasks as independent full-review batches.
- The merged plan is the only plan Codex executes.

## Phase 4: Codex Execution

- Follow `12-plan-merged.md` before improving it.
- Keep changes inside scope.
- Use TDD for behavior changes.
- Preserve unrelated dirty worktree changes.
- Do not mix unrelated files into commits.
- If a plan asks for a commit and the worktree is dirty, stage only the safe subset or record `commit skipped: <reason>`.
- If an optional task is skipped, use the exact marker:

```text
SKIP: <task-id> reason=<one-line reason> blocker=<dependency or "none">
```

## Phase 5: Execution Report

Write `20-execution-report.md`:

```markdown
## Source
## Scope
## Changed Files
## Task Status
- task-id: done/skipped/blocked
  Evidence:
## Verification
- command -> key output
## Artifacts
- screenshots / JSON / downloaded files
## Git State
- branch
- staged
- untracked relevant files
- commit
## Known Gaps
```

Do not overstate. Generated screenshots are not the same as inspected screenshots.

## Phase 6: Dual Review

Produce reviews independently:

- `30-review-claude.md`: Claude CLI read-only review.
- `31-review-codex-subagent.md`: Codex subagent review in isolated context.

Neither review should read the other. Both should use:

```markdown
## Source
## Findings
- P0/P1/P2/P3: title
  Claim:
  Evidence:
  Why it matters:
  Suggested action:
## Criteria Check
```

## Phase 7: Arbitration And Repair

Write `40-arbitration.md`. It must enumerate every P0/P1 finding from both reviews.

Decision labels:

- `accept Claude`: Claude finding is correct; fix or record the gap.
- `accept Codex`: Codex finding is correct; fix or record the gap.
- `reject both`: neither model's claim is correct or in scope; cite counter-evidence.
- `third path`: real issue but suggested fix is not the smallest safe path.
- `defer`: valid but optional, blocked, or intentionally outside this phase.
- `needs more evidence`: potentially valid, but current artifacts are insufficient.

Hard evidence rules:

- Weak evidence cannot be the sole basis for `accept`.
- Decisions must cite artifact evidence, not model identity.
- Every accepted P0 requires strong evidence.
- A P0 endorsed by both Claude and Codex subagent cannot be rejected without `path:line` counter-evidence.
- `needs more evidence` means arbitration gathers evidence or stops; it must not average model opinions.
- `not verified` means unchecked, not correct.

## Stop Rules

- For every T2+ route, define done check, max rounds, budget cap if known, and hard-stop risks before execution.
- Maximum 2 repair iterations per brief.
- On the third new P0, write `loop-limit-reached` and stop for user input.
- Any unresolved P0 blocks final report.
- P1 must be fixed, deferred with a named reason, or disputed with resolution notes.
- P2 may ship only if fixed or explicitly deferred.
- P3 may be recorded without blocking.
- If Claude and Codex subagent both mark the same issue P0 and Codex cannot disprove it with strong evidence, stop for user decision.
- Stop or checkpoint when the strategic direction changes, when no new evidence appears after repeated repair, when production/destructive risk appears, or when the route tier no longer matches the task.

## Final Report

Write `50-final-report.md` only when stop rules pass.

Include:

- final status
- changed files
- review findings and dispositions
- verification output
- artifact paths
- git state
- residual risks

## Evidence Standards

Strong evidence:

- Code: `path:line` plus exact symbol or selector.
- Tests: full command and pass/fail count.
- UI/browser: screenshot path plus visual inspection statement; DOM checks for dynamic linkage.
- Files/downloads: path, size, type check, checksum when useful.
- Git: `git status --short`, branch, staged files, commit SHA.

Weak evidence:

- static UI copy as backend linkage proof
- model citations without reopening files
- screenshots generated but not inspected
- tests that do not execute the changed file

## Chat Output

For quick arbitration:

```markdown
**Verdict**
<short judgment>

**Findings**
- accept/reject/third path/defer: <claim> — <evidence>

**Next Actions**
- <fix or record>
```

For full loop work, create/update artifacts unless the user asks for inline-only work.

## Forward Tests

For reusable pressure scenarios and leak hygiene, read `references/forward-tests.md`. Forward-test prompts must look like real tasks and must not leak expected answers, intended fixes, or prior conclusions.

## User Checkpoints

For user calibration points, degraded Claude-required flow, and Codex-only independent-review fallback, read `references/user-checkpoints.md`.

## Skill / Plugin Promotion

Promote a repeated loop pattern to a skill or plugin only after the stable parts are known. Default threshold: 10+ repeated uses, or fewer only when risk/cost is high and the pattern is already stable.

Promotion requires:

- stable context pack;
- route trigger;
- done check;
- checker or harness when practical;
- examples or forward tests;
- known failure modes;
- stop rules.

Do not turn a one-off project lesson into a skill unless it generalizes beyond that project.

## Common Mistakes

- Treating `loop-engineering` as "always create multiple agents" instead of choosing a route tier.
- Starting execution before defining the strategic "good enough" target.
- Writing tactical or execution plans when the strategic target is still unclear.
- Creating lanes for role aesthetics rather than boundary value.
- Missing one of the six interfaces: goal, state, context, act, capture, stop.
- Running this full loop for tiny edits.
- Running full dual review after every tiny internal helper during a large planned refactor instead of batching by product surface or contract boundary.
- Letting Claude plan replace Codex's repository-grounded judgment.
- Treating planning as a one-way model artifact instead of calibrating unclear goals, UX expectations, and acceptance criteria with the user.
- Executing one plan before the merged plan exists.
- Letting reviews read each other and converge artificially.
- Calling Codex subagent feedback Claude review.
- Pretending Claude reviewed when CLI failed.
- Cold-starting Claude for every helper-level patch or ordinary batch as if it were CI.
- Treating a reused Claude companion discussion as a fresh independent review.
- Starting a fresh Claude planning/design conversation every time without checking for a reusable Claude companion lane.
- Reusing a planning/design Claude session for independent review, adversarial critique, or any quality gate where freshness matters.
- Leaving old Claude sessions open with no recorded `next_expected_use` or `close_or_keep` decision.
- Leaving completed Claude/Codex review lanes unarchived after valid review artifacts land and `next_expected_use: none`.
- Continuing past a missing required Claude plan/review as if the dual-model gate succeeded.
- Treating Codex-only fallback as lower quality by default instead of using independent Codex subagents or isolated Codex contexts with explicit degraded markers.
- Replacing unavailable Claude review with current-thread self-review instead of launching independent Codex subagent reviewer(s) when subagents are available.
- Missing skip markers.
- Claiming generated screenshots were visually inspected.
- Committing unrelated dirty files.
- Relying on chat history instead of artifacts as loop memory.
- Sending unstructured cross-lane "continue" messages.
- Repeating large plan/report bodies in handoffs instead of sending artifact paths and read requirements.
- Giving every lane broad project context when only planning needs it.
- Skipping `thread-ledger.md` rows for `send_message_to_thread`.
- Skipping agent worklog entries, losing lessons and repeated pitfalls.
- Making the manager lane the central relay for all messages instead of letting lanes hand off directly.
- Treating the bootstrap thread as a main agent instead of assigning a real lane role.
- Starting a new lane set for a correction to the active loop instead of messaging the existing owner lane.
- Auto-archiving lane threads before the user has finished evaluating the loop.
- Creating all lanes for small work where one thread is enough.
- Treating worklog as enough when context is nearly full; drop a baton for unfinished recoverable state.
- Letting auto-compact happen without a baton when exact next steps, dead ends, or dirty git state matter.
- missing `claude_policy` in a loop message or lane artifact.
- Closing out required Claude without the required artifact or a real `claude-unavailable` marker.
- Letting a hung Claude CLI recovery require process inspection or kill permissions instead of writing an unavailable marker after the policy wait.
- Dispatcher running Claude for a lane instead of the lane owning its own Claude use.
- Silently skipping conditional Claude without `Claude skipped: <reason>`.
- Handoff rewrites or summarizes a complete artifact body instead of sending the artifact path and read requirement.
- Polling long-running lane threads every few seconds instead of using artifact checks, `check_after`, deadlines, and one recovery read only after a missed window.
- Sending every accepted review finding back to planning instead of letting arbitration repair in-scope implementation defects.
- Running full dual review for every helper-level patch instead of reviewing larger phase/product/contract slices.
- Starting the next tiny execution slice immediately after arbitration when a larger user-visible workflow loop should be grouped and reviewed once.
- Treating a user rejected preview as an ordinary technical review finding instead of a product/UX checkpoint that may supersede the route.
- Leaving stale heartbeat/monitor automations active after a route, artifact path, or lane has been superseded.

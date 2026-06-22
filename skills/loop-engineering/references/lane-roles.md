# Lane Roles Reference

Use this reference when a loop needs named lanes, cross-thread handoffs, manager/dispatcher recovery, or role-specific context rules. Lanes are reusable role contracts: the same orchestration pattern can support coding, research, video production, writing, product design, or other long-running projects.

## Core Principle

Artifacts are the shared memory. Chat history may help a lane think, but cross-lane coordination must flow through explicit artifacts, ledgers, worklogs, and handoffs.

Treat orchestration as event/state driven. Inspired by manager-style agent frameworks and graph workflows, the manager tracks lane state, deadlines, and artifacts; it should not continuously read worker conversation just to feel current.

For multi-round or multi-lane loops, use `state-feedback-schema.md` to record how capture changes the next prompt, context, owner, or action. Feedback is not just a review comment; it is a recorded state transition.

## Role Types

| role | purpose | typical artifact |
|---|---|---|
| planning / product / producer | understand goal, gather context, pressure-test routes, create merged plan | plan, design spec, brief |
| execution / maker | implement the accepted plan inside scope | execution report, changed files |
| review / QA | independently critique execution against plan and evidence | review findings |
| arbitration / editor-in-chief | adjudicate findings, repair accepted issues, close the phase | arbitration, repair report, final report |
| manager | audit status, recover lost state, select next phase, maintain coordination | worklog/ledger updates |
| dispatcher | physically sends messages, creates/continues threads, monitors artifacts | ledger rows, handoffs |

For non-code workflows, map roles to the task instead of forcing coding labels. Example video workflow: topic planner -> researcher -> scriptwriter -> visual planner/editor -> QA/reviewer -> publisher, with manager/dispatcher coordinating artifacts. The durable value is reusable role memory and artifact flow inside Codex, not the specific plan/execute/review labels.

## Human-Readable Lane Naming

Lane names, thread titles, branch names, and worktree folder names are part of
the product surface for human operators. Manager/dispatcher must choose short,
stable, human-readable names before creating or continuing lanes.

Rules:

- Prefer `role + letter/number + purpose`, not long artifact slugs or opaque
  generated ids.
- Keep visible thread titles short enough to scan in a sidebar: usually 3-6
  words.
- Include the work type first: `Plan`, `Exec A`, `Exec B`, `Review`, `Arbitrate`,
  `Repair A`, `QA`.
- Include the human purpose second: `Shell Pocket`, `Paper Mode`, `PPT Region`,
  `Agent Panel`, `Safety QA`.
- Use compact branch/worktree names such as `codex/b12-a-shell-pocket`,
  `codex/b12-b-paper`, `codex/b12-c-ppt`, `codex/b12-integrator`, and
  `codex/b12-repair-a-paper`.
- Record machine ids separately in the ledger. Do not make humans infer purpose
  from thread ids, pending worktree ids, UUIDs, or full artifact filenames.
- If a tool creates a pending worktree/thread with an opaque id, immediately map
  it to a human label in the ledger and rename the visible thread when the tool
  supports it.

Examples:

| lane | good visible title | good branch | avoid |
|---|---|---|---|
| main integration | `Exec Integrator - B12` | `codex/b12-integrator` | `019eef...` |
| shell/pocket | `Exec A - Shell Pocket` | `codex/b12-a-shell-pocket` | `batch12-parallel-preview-first-research-workflow-shell-pocket-relaunch` |
| paper | `Exec B - Paper Mode` | `codex/b12-b-paper` | `worktree-lane-b-phase2-batch12-paper-manuscript-mode` |
| arbitration | `Arbitrate - B12 Repair` | `codex/b12-arbitration` | `standing-arbitration-lane-019eeec2` |

## Lane Reuse Policy

Lanes are persistent roles when continuity helps: planning/product, execution, arbitration/repair, manager, and dispatcher may reuse an existing visible thread for the same loop if the thread is not blocked, polluted by incompatible scope, or too stale to recover. Reuse is preferred when the lane benefits from local project memory and repeated setup would waste context.

Use a fresh thread/session when independence is the point: Claude review, Codex independent review, adversarial critique, or any second-opinion lane that must not inherit implementation or arbitration bias. Review freshness is a quality gate, not a habit.

For Claude specifically, choose and record `claude_session_mode: fresh | reuse | one_shot` before dispatch. Planning/product/design Claude may be a reusable companion lane when the same strategic or UX conversation is continuing. Review Claude must stay fresh and bounded. Smoke tests and single bounded checks should be `one_shot`.

Manager/dispatcher must record the choice. A new thread ledger row should state why reuse was not chosen. A reuse handoff should be structured like any other loop message and must include source artifacts, boundaries, output artifacts, `check_after`, `deadline`, and blocker signals.

When a Claude task closes, the owner lane or dispatcher records `next_expected_use` and `close_or_keep`. Close/archive lanes with no expected follow-up; keep only lanes with a named future use. Do not let old Claude planning/design sessions become hidden state for review or arbitration.

### Independence And Physical Dispatch

Independence is a context boundary, not only a file name.

- Formal independent planning uses at least two judgment contexts that start
  from the same brief/context pack. Claude planning must not see the Codex plan,
  and Codex planning must not see the Claude plan, before both artifacts exist.
- If one planning lane writes its own plan and later asks Claude for feedback,
  that Claude output is a critique, pressure test, or route comparison. It is
  not an independent Claude plan unless the prompt and lane were isolated from
  the earlier plan.
- A dispatcher or Claude launcher/helper may perform mechanical delivery:
  creating packets, launching a named Terminal lane, checking done JSON,
  validating headings, and recording lifecycle. That helper must not make
  planning, review, merge, or arbitration judgments.
- Manager/dispatcher may launch fresh review threads or subagents, but it must
  not write the review in the manager context or treat manager reasoning as
  independent evidence.
- When UI/tooling only exposes a Codex subagent instead of a visible thread,
  the subagent is acceptable as an isolated review/planning lane if the prompt
  is bounded, it does not read sibling artifacts before allowed, and it writes a
  formal artifact. Record that route in the ledger.

For local Claude Terminal lanes, lifecycle is a dispatch gate. Before opening a
Claude lane, manager/dispatcher must check the launcher registry/window status
and decide: reuse existing companion, fresh independent review, one-shot, or no
Claude. A handoff that omits `claude_lane_id`, `lane_role`,
`loop_id`, `lane_scope`, `reasoning_tier`, `claude_session_mode`,
`next_expected_use`, and `close_or_keep` is incomplete. Reuse matching is based
on the full route key:
`cwd + loop_id + lane_role + lane_scope`; related but different topics need
different scopes. After artifacts validate, close no-future-use lanes before
launching more Claude work.

For active product/strategy planning, the default is one stable Claude companion
scope per major workstream, reused across adjacent batches. Do not split the
same ongoing writing-IDE/product-direction discussion into batch-numbered
one-shot planning lanes. A new planning Claude lane needs a recorded reason:
the old companion is stale, blocked, polluted by incompatible context, the topic
is genuinely separate, or the user explicitly wants a fresh second opinion.
Batch-specific plan artifacts should be written by the stable companion where
possible; artifact freshness does not require conversation freshness.

### Claude Terminal Lanes

On local macOS/Codex, Claude lanes run through visible named Terminal sessions,
not bridge scripts or hidden direct stdin. The launcher shape is:

```bash
claude --name <claude-lane-id> --permission-mode bypassPermissions \
  "Read and execute this packet exactly: <packet-path>"
```

Rules:

- Lane identity lives in the Claude `--name`, the packet `lane_id`, the output
  artifact, the done JSON, and the ledger row.
- Lane state also lives in the launcher registry. Use `--list` or `--status`
  before launch when deciding reuse versus a fresh lane.
- Launch Claude Terminal lanes from a stable, trusted project `cwd` whenever
  possible, such as the loop workspace root or the implementation project root.
  Do not launch from `/tmp`, a scratch packet directory, a transient generated
  folder, or a newly created worktree unless the handoff explicitly needs that
  directory. Claude's workspace-trust prompt is directory-scoped and may appear
  before permission mode is applied; using stable trusted roots avoids repeated
  manual Yes/No prompts. Pass packet paths and source artifact paths as absolute
  paths, and use narrow `--add-dir` only when Claude truly needs additional live
  path access.
- Use a persistent named Terminal lane only for planning/product/design
  companion work where continuity is valuable.
- Use a fresh named Terminal lane for formal Claude review, adversarial critique,
  or second opinion. Do not reuse companion lanes for review gates.
- Planning/product/design companion lanes are continuity lanes. Do not mark them
  `fresh + close + next_expected_use: none` merely because one plan artifact
  landed. If the lane may support the same product/strategy discussion later,
  record `claude_session_mode: reuse`, name the next expected planning/product
  use, and set `close_or_keep: keep|checkpoint`. If there is truly no future
  use, call it a `one-shot` consultation instead of a companion.
- For a reusable companion lane, send follow-up packets to the existing named
  Terminal lane with `--reuse`; do not open duplicate windows for the same
  lane id. Do not open duplicate companion windows for the same route key
  (`cwd + loop_id + lane_role + lane_scope`) unless the previous lane is stale,
  blocked, polluted, or intentionally replaced with a ledger reason.
- For a completed fresh/review/one-shot lane, close the named Terminal lane
  after output/done validation and ledger/worklog capture. Use the launcher
  `--close` option; it interrupts matching lane TTY processes before closing so
  Terminal does not show a running-process confirmation dialog.
- A close is valid only after verification. The launcher should normalize TTY
  names, terminate matching `claude`/`caffeinate` processes, verify that no
  matching process remains, close the matching Terminal window, and verify the
  window disappeared. Matching must use durable evidence: lane title, tab custom
  title, tab history, registered TTY, and registered window id. Terminal often
  falls back to a generic `-zsh` title after Claude exits; that idle shell is
  still the lane window and must be closed or recorded as `close_failed`. If
  either process or window remains, record `status: close_failed` with evidence;
  do not record `closed`.
- Do not close planning/product/design companion lanes merely because a single
  plan artifact landed when `next_expected_use` names a future strategy,
  product, UX, or route-comparison use. Leave them open with
  `close_or_keep: keep|checkpoint`. macOS may warn that `claude` or `caffeinate`
  is still running if a kept companion Terminal window is manually closed; that
  is expected and should not be treated as a lane cleanup requirement.
- Claude writes the requested output artifact plus done JSON. Manager/dispatcher
  monitors those files, not terminal chat.
- `dontAsk` may block file writes; local Terminal lanes default to
  `bypassPermissions` when the lane must write artifacts.
- A lane is not complete until output is non-empty, required headings are
  present, done JSON has the expected `lane_id` and `status: done`, and the
  result is recorded in ledger/worklog/state feedback as needed.
- A lane is not cleanly closed until its lifecycle (`next_expected_use` and
  `close_or_keep`) is recorded and any no-longer-needed Terminal window is
  closed.

### Claude Companion Lane

A Claude companion lane is a reusable planning/product/design conversation, not a
formal review gate. Use it when continuity helps: recurring product direction,
UI taste, user calibration, strategy pressure tests, multimodal/manual-style
discussion, or repeated route comparison.

Rules:

- Prefer continuing an existing healthy companion lane over cold-starting Claude for
  every product/design question.
- Use a durable product/workstream `lane_scope`, not a batch-numbered scope, when
  the same companion will guide multiple adjacent execution batches.
- Keep companion prompts decision-oriented: current strategy, recent artifact, user
  feedback, candidate next action, specific risks/questions. Do not dump the whole
  repository by habit.
- Companion output is advisory until summarized into an artifact with source paths,
  accepted/rejected decisions, and next-context deltas.
- Do not use companion output as an independent review. If the next gate requires
  independent review, open a fresh bounded Claude review lane.
- Do not invoke companion Claude for low-risk helper fixes or routine implementation
  churn; use Codex tests/review/arbitration instead.
- Record `next_expected_use` such as `continue UI strategy after next screenshot` or
  `continue product direction after user checkpoint`. If no next use exists, close it.

## Lane Cleanup And Archiving

Lane lifecycle is part of dispatch, not optional UI housekeeping. After any lane
artifact lands and passes required heading/evidence checks, manager/dispatcher
must record one of:

```text
next_expected_use: none
close_or_keep: close
```

or:

```text
next_expected_use: <specific future use>
close_or_keep: keep | checkpoint
```

Default decisions by lane:

- **Claude review / Codex independent review / adversarial critique / second opinion**:
  one-shot. Archive after the review artifact is valid and ledger/worklog completion
  is recorded. Do not keep these lanes for later phases; independence requires a
  fresh bounded lane next time.
- **Execution**: keep when the same loop will continue implementing related
  product/contract slices and the thread is not stale, blocked, or polluted by
  incompatible scope. Archive only after the broader milestone is complete or a
  replacement execution lane is chosen.
- **Arbitration/repair**: keep as a standing role for active T3/T4 product loops,
  especially when the same milestone will continue through more execution,
  review, and repair. After a phase final report lands, record
  `next_expected_use: continue arbitration/repair for active loop` and
  `close_or_keep: keep` unless the broader milestone is actually closed.
  Archive arbitration only when the full milestone closes, a replacement lane is
  confirmed, the lane is corrupted/stale, or the user explicitly asks. Do not
  archive merely because one batch's final report exists.
- **Planning/product/design**: keep only when a concrete next product/strategy/UX
  use is named. Archive when the plan/consultation has been absorbed into a formal
  artifact and no follow-up is expected.
  For active product loops, default to `close_or_keep: checkpoint` instead of
  close when the user is still shaping strategy or the next batch likely needs
  the same companion context. Close only after recording `next_expected_use: none`
  or when the next phase requires independence rather than continuity.
- **Manager/dispatcher**: keep for the active loop, unless the user explicitly
  pauses, cancels, or moves the loop elsewhere.

If a completed lane remains visible without a named future use, treat that as a
coordination defect: update the ledger/worklog, archive it, and avoid using it as
implicit state.

## Planning Lane

Planning is allowed to be context-heavy. It should read more of the project than other lanes, because a weak plan makes later execution and maintenance worse.

Planning lane should:

- read the brief, prior final reports, specs, relevant code/project structure, and domain workflow skills;
- define the strategic end-state, "good enough" target, non-goals, and stop condition before tactical or execution planning;
- split large plans into strategic, tactical, and execution layers when the user goal is broad or likely to expand;
- ask targeted user checkpoints when goals, UX expectations, phase boundaries, or acceptance criteria are unclear or likely to drift;
- use Claude as a deep planning partner when risk is high;
- allow iterative Claude discussion for planning, route comparison, and pressure testing;
- summarize any discussion into formal artifacts, not rely on hidden chat memory;
- produce a merged plan with accepted/rejected/third-path decisions.

Planning Claude may use a larger bounded context bundle and multiple turns. This is different from review Claude, which should be fresh and independent.

### Parallel Dual Planning

When a loop requires Claude + Codex plans:

- Manager/dispatcher should prepare one brief/context pack and dispatch Claude
  planning and Codex planning as separate judgment lanes as close to parallel as
  the tools allow.
- The Codex planning lane should not block on doing all of its own planning
  before Claude is launched. That turns independent planning into a slower
  serial pressure test and risks contaminating Claude with Codex conclusions.
- The Claude lane may be launched by a mechanical dispatcher/helper, but the
  helper only sends the packet and validates artifacts. It does not plan or
  merge.
- The merge lane reads both completed plans and writes accepted/rejected/third
  path decisions. The merge lane is the first place where cross-plan comparison
  is allowed.
- If independent parallel dispatch is impossible, mark the limitation in the
  artifacts, classify any later Claude output honestly, and use the
  degraded-mode checkpoint rules before treating the result as dual-model
  planning.

### Planning Lane Hard Boundary

Planning is not execution. A planning lane must not implement the plan it writes,
even when the implementation appears straightforward, the user says "continue",
or the user corrects the plan midstream.

Allowed planning-lane writes:

- briefs, Claude/Codex/merged plans, design specs, strategy/tactical/execution
  contracts, prompt packets, unavailable markers, validator outputs, worklogs,
  ledgers, state-feedback, and other control-plane artifacts;
- small repairs to those planning/control artifacts, such as adding missing
  `stop_condition`, `expected_artifacts`, `check_after`, `deadline`, or
  `blocker_signal`.

Forbidden planning-lane writes:

- production Python/TypeScript/React/source files;
- frontend components, CSS, generated app data, tests, package/config files,
  runtime scripts, vault notes, templates, project folders, git state, commits,
  or pushes;
- any TDD red/green cycle, app build/test run for implementation, dev server, or
  browser preview intended to validate a code change.

Interpretation rule:

- In a planning lane, "continue", "按计划继续", "go on", "fix it", or a user
  correction means continue planning, research, Claude consultation, merged-plan
  repair, validator repair, or checkpoint writing.
- It does not authorize execution unless the user explicitly says to switch the
  current lane into execution and names the implementation scope, or a
  manager/dispatcher sends a separate execution-lane handoff.

If the planning lane discovers that the next useful action is implementation, it
must write an execution handoff/contract and stop for manager/user dispatch. It
must not start editing implementation files itself.

If the planning lane violates this boundary, the recovery rule is:

1. Stop immediately.
2. Revert only the planning lane's own out-of-scope implementation edits, without
   reverting unrelated user or lane work.
3. Record the boundary violation and recovery in the worklog/state-feedback when
   appropriate.
4. Return only to planning artifact repair or checkpoint.

## Execution Lane

Execution follows only the merged plan. It should not casually reopen product direction.

Execution lane should:

- keep changes inside the accepted phase boundary;
- use TDD for behavior changes where practical;
- write one execution report for the whole product/contract slice;
- use Claude only conditionally for plan gaps, source-policy uncertainty, or risk-boundary questions;
- record `plan-gap: <reason>` if the merged plan cannot be safely executed.

For large refactors, use fewer, larger execution phases that land a user-visible workflow state or durable data contract.

### Execution-Owned Subagents

For large execution slices, the execution lane may use its own subagents to improve
throughput. This is different from manager-created review/planning lanes: these
subagents are implementation helpers owned by the execution lane, not separate
loop phases.

Dispatcher requirement:

- Every handoff to an execution lane for a large execution slice must include
  `execution_owned_subagents: allowed|not_needed|forbidden`.
- Use `allowed` by default when the slice contains separable data/model, UI
  component, styling/responsive, test, docs, fixture, or screenshot work.
- Use `not_needed` only when the task is narrow enough that helper split would add
  more coordination overhead than value.
- Use `forbidden` only when a safety, isolation, or user constraint requires one
  executor; record the reason in the handoff and ledger.
- If `allowed`, the prompt should explicitly say the execution lane may use
  execution-owned subagents to improve efficiency, choose the split itself, keep
  helpers inside scope, integrate results, run verification, and write one
  consolidated execution report.

Use execution-owned subagents when the execution slice contains separable work such
as data/model changes, UI components, styling/responsive behavior, tests, docs, or
fixture generation. The execution lane decides whether to use them and how to split
the work. The manager should not micromanage these helper subagents.

Rules:

- Keep every helper inside the execution contract, write scope, and stop condition.
- Do not turn helper subtasks into full plan -> review -> arbitration loops.
- The execution lane remains responsible for integration, conflict resolution, tests,
  verification, and one consolidated execution report.
- The execution report should state whether subagents were used and what each contributed.
- If a helper discovers a plan gap, scope change, mutation/runtime need, or product-direction
  mismatch, the execution lane records the blocker and stops instead of silently expanding scope.

### Parallel Worktree Execution Lanes

For large T4 execution slices, manager/dispatcher may split implementation across
isolated worktrees instead of asking one execution lane to do everything. Use this
when the work naturally separates by product surface, data/model contract,
runtime boundary, fixture set, visual QA surface, or test/evidence layer.

Default shape:

```text
Main Integrator lane
  owns shared contracts, final merge/integration, full verification, consolidated report

Parallel Worktree lanes A/B/C/...
  each owns one isolated worktree/branch, one write scope, one lane report

Late QA/Safety lane
  starts only after lane outputs or an integrated preview exist
```

Manager/dispatcher contract requirements:

- name every worktree path, branch, lane role, write scope, and forbidden scope;
- forbid concurrent edits to the same checkout/worktree;
- require the integrator to define shared component/data/CSS boundaries before
  parallel lanes depend on them, or explicitly state the stable boundaries from
  existing code;
- give each lane one expected artifact path and focused verification commands;
- require lane reports to include touched files, tests run, known conflicts,
  remaining integration work, safety check, and lifecycle;
- require the integrator to consume lane reports/diffs, resolve conflicts, run
  focused then full tests/build/browser evidence, and write one consolidated
  execution report;
- state the integration order, such as shell/data boundary -> feature surface A
  -> feature surface B -> Agent/interaction -> QA/safety.

Parallel lane rules:

- A lane may edit only its assigned worktree and write scope.
- A lane must not modify the product root, sibling worktrees, shared Git state,
  or another lane's report.
- A lane must not stage, commit, push, reset, stash, or run destructive cleanup
  unless that operation is explicitly authorized in the handoff.
- If a lane accidentally edits outside its worktree/scope, it must stop,
  compare evidence, recover only clearly attributable out-of-scope edits, and
  record `Boundary Incident / Recovery` in its report. If attribution is
  uncertain, stop and escalate to manager instead of reverting.

Integrator rules:

- The integrator is the only lane that merges/selects patches from parallel
  lanes.
- The integrator must not invent completed lane work when lane reports or diffs
  are absent; it records blockers or partial integration honestly.
- The consolidated execution report must distinguish lane-local verification
  from integrator verification, and must include git/worktree state for the
  integration worktree plus any relevant boundary incidents.

## Phase Sizing And Review Cadence

For substantial long-running work, spend more effort in planning and reduce review churn during execution.

Planning should define:

- the strategic target and evidence that proves the target is "good enough" for this loop;
- tactical workflow slices before execution tasks;
- phase boundaries such as Phase 3A/3B/3C;
- the user-visible workflow loop each phase is meant to land;
- data contracts and state transitions;
- acceptance criteria and verification commands;
- explicit out-of-scope items;
- when the next dual review is required.
- user-calibrated assumptions: what the user cares about, what they do not want, and what would make the delivered workflow feel wrong even if tests pass.

If planning cannot state the strategic target, write `strategy-gap: <missing decision>` and stop for a user checkpoint. Do not compensate by writing a longer execution task list.

Execution should group work into larger slices when the pieces belong to the same user workflow. Example for a biology learning workbench: daily guide/status command center, acquisition refresh facade, queue lifecycle commands, weekly project refresh, and PPT readiness command/report may be grouped into one or two coherent execution slices instead of five helper-sized review loops.

An execution slice is too small for a full review loop when it only changes one helper, one internal function, or one local cleanup without landing a visible workflow state, product surface, durable contract, migration boundary, or risk boundary.

For frontend/product-surface slices, planning must define the visible UI shape before implementation: target screen, layout zones, expected cards/panels/controls, placeholder or degraded backend states, and the user calibration point. When the user must judge the interface, prefer a visible skeleton or prototype surface first, then wire deeper backend/runtime behavior in a later slice.

### Frontend Calibration And Product Fit

Frontend/product slices have two separate gates: technical validity and product fit. Passing tests, screenshots, or review does not prove the surface matches what the user meant by "useful" or "intuitive."

Rules:

- The execution contract should name the primary work object and visible workflow, not only status/readiness cards. If existing UI is moved or demoted, state where it will live after the change.
- Stop at the preview URL/screenshot when user judgment is part of acceptance. Do not continue to backend wiring, full review, or the next batch until the user accepts the visible direction or the handoff explicitly says otherwise.
- If the user rejects the visible shape after preview, review dispatch, or even after technical review passes, treat it as a product/UX target miss. Pause ordinary arbitration and backend continuation, write a correction or superseding strategy artifact, update state/feedback, and route planning/design before more implementation.
- Use bounded design critique when useful: screenshot, touched components/styles, design constraints, and the intended workflow. Do not ask a design critic to rediscover the whole project.
- Record the calibration outcome in state/feedback so later lanes know whether the visual direction is approved, superseded, or still pending.

Review cadence:

- Run local tests and write execution reports during intermediate implementation.
- Do not run full Claude + Codex review for every helper-level or command-only patch.
- Run full independent review when a user-visible workflow loop, product surface, or stable data contract has landed.
- Keep full review for security/data-loss/legal-source-policy risks even if the code slice is small.
- If an intermediate patch reveals a plan-gap or direction change, stop for planning/user checkpoint before continuing.

Manager/dispatcher cadence:

- Track artifact paths, lane state, deadlines, and blockers.
- Do not read execution threads for routine progress.
- After an arbitration closes, consider whether the next work should be grouped into a larger execution slice before dispatching another small lane handoff.
- If the user has repeatedly asked for faster progress or larger batches, the
  manager must not propose a narrow hygiene/helper/safety-cleanup slice as the
  next main batch unless it is an unresolved blocker. Fold those concerns into a
  larger product/workflow execution contract and verify them inside that batch.

## Review Lane

Review must be independent. Review Claude should normally be a new session, not a continuation of planning Claude.

Review lane should:

- read the merged plan, execution report, test output, changed files/diff, and relevant complete functions;
- use a bounded evidence bundle that is accurate enough for real review;
- not read the other review before both reviews are complete;
- focus on bugs, regressions, missing tests, evidence-boundary violations, and user workflow failures;
- write findings with severity, claim, evidence, impact, and suggested action.
- close with `next_expected_use: none` and `close_or_keep: close` unless the user
  explicitly asks for a continued review discussion. Even then, the continued
  discussion must not be reused as a fresh independent review for a later phase.

Do not rely on old planning-Claude memory for review. If Claude needs project understanding, put that understanding in the review context bundle.

Manager/dispatcher review rules:

- The manager thread does not perform formal review. It dispatches review lanes,
  validates review artifacts, records lifecycle, and routes arbitration.
- A Codex review must be a fresh visible review thread when practical, or an
  isolated Codex subagent when that is the available independent route. In both
  cases it needs its own bounded prompt, output artifact, and lifecycle record.
- A Claude review must be a fresh named Terminal lane with `next_expected_use:
  none` and `close_or_keep: close` unless the user explicitly asks for a
  continued review discussion. It must not reuse a planning or companion Claude
  lane.
- If Claude is unavailable, the fallback is not manager self-review. Use
  independent Codex review lane(s)/subagent(s) or stop for degraded-mode
  approval, as described in `user-checkpoints.md`.
- After valid review artifacts land, close/archive no-future-use review lanes.
  Do not leave them as hidden state for later phases.

## Arbitration Lane

Arbitration decides by evidence, not by model identity.

Arbitration lane should:

- enumerate every P0/P1 finding from both reviews;
- accept, reject, defer, or request more evidence with path/command/artifact support;
- repair accepted findings as coherent contract patches, not one tiny helper at a time;
- run targeted and required verification;
- write final report only when stop rules pass.
- stay reusable for the active loop unless the full milestone closes, a replacement
  lane is confirmed, the lane is corrupted/stale, or the user explicitly asks.

### Parallel Arbitration / Repair Worktrees

Large repair phases may use isolated worktree repair lanes, but adjudication
authority stays centralized. Use this when accepted findings span separable
surfaces, many files, or conflicting patches that would overload one arbitration
thread.

Default shape:

```text
Chief Arbitration lane
  owns findings disposition, repair contract, integration, final report

Repair Worktree lanes A/B/C/...
  each owns one accepted finding group or product surface

Optional QA/Safety lane
  checks integrated repairs after the chief arbitration lane has a preview
```

Rules:

- Only the chief arbitration lane decides finding disposition:
  `accept`, `reject`, `defer`, `third path`, or `needs more evidence`.
- Repair lanes may implement only already-dispositioned, scoped repairs. They do
  not independently reinterpret review findings or expand product direction.
- Each repair lane needs its own worktree/branch, write scope, expected repair
  report, focused verification, known conflict list, and stop condition.
- The chief arbitration lane alone integrates repair outputs, resolves
  conflicts, runs required verification, and writes arbitration/final artifacts.
- If repair lanes reveal a plan gap, scope change, or uncertain evidence, they
  stop and report back to chief arbitration. The chief lane decides whether to
  gather evidence, return to planning, or defer.
- Boundary incidents follow the same rule as execution worktrees: recover only
  clearly attributable out-of-scope edits and record the incident in the repair
  report, ledger, and final arbitration summary.

## Repair Routing

After review finds a problem, route it by defect type:

| defect type | owner | action |
|---|---|---|
| implementation defect inside the merged plan | arbitration | accept/reject, repair, verify |
| missing test/evidence for planned behavior | arbitration | add focused test/evidence or defer with reason |
| unclear evidence | arbitration | gather evidence or mark `needs more evidence`; do not average opinions |
| plan cannot satisfy the brief | planning | write `plan-gap: <unsatisfied goal>` and return to planning/user |
| fix changes scope, product direction, architecture, or data contract beyond the phase | planning | stop repair, open a planning update or next phase |
| user-goal mismatch discovered during review | planning / user | stop for clarified brief before more execution |

Default rule: arbitration repairs in-scope implementation defects. Do not send ordinary accepted review findings back to planning. Planning reopens only when the accepted finding proves the merged plan itself is wrong, incomplete, or unsafe to execute.

For borderline findings, arbitration may choose `third path`: keep the current phase scope, make the smallest contract-safe repair, and defer broader redesign to the next planning phase.

## Manager Role

Manager is a status and recovery role, not a boss model.

Manager should:

- inspect artifacts and ledgers to know where the loop is;
- detect missing, empty, stale, or malformed artifacts;
- decide whether to route planning, execution, review, or arbitration next;
- update worklog/ledger when process lessons emerge;
- read state/feedback events before worker chat when diagnosing repeated failures or deciding the next handoff;
- check for reusable Claude planning/product/design companion lanes before opening a new Claude session, while keeping review Claude fresh;
- resolve non-blocking planning checkpoints itself when the user already
  participated in the plan, the validator/required gates passed, the plan stays
  inside the accepted strategy, and no scope/risk uncertainty remains; record the
  decision and dispatch the execution lane instead of asking the user again by
  reflex;
- keep monitoring active loops when the user asks it to keep moving.

Manager must not silently execute business-code changes, overrule arbitration without evidence, or centralize all lane communication as hidden chat.

### Manager / Planning Lane Rotation

Long-lived manager and planning lanes can become coordination debt when chat
history accumulates old heartbeats, closed batches, stale lane ids, and
superseded routes. Rotate them deliberately before context corruption affects
dispatch.

Rotate a manager or planning lane when any of these are true:

- repeated context compression or interrupted turns make current state
  unreliable;
- old route instructions, obsolete heartbeats, or stale lane ids keep resurfacing;
- the lane has accumulated multiple completed phases and the next phase needs a
  clean dispatch context;
- the user reports the manager/planner is stuck, slow, confused, or reviving old
  work;
- the lane is near context limits and exact dirty state, active lanes, or
  blockers matter.

Rotation contract:

- Write a baton/context pack before handoff. It must include loop id, roots,
  canonical artifacts, active lanes, retired lanes, current phase status,
  pending expected artifacts, safety boundaries, stale monitors to delete/update,
  dirty git/worktree state, and next routing decision.
- Record the rotation in state-feedback, worklog, and thread-ledger.
- Mark the old manager/planning lane retired, archived, or checkpointed with
  `next_expected_use: none` unless a specific future use is named.
- The new lane must start artifact-first from the baton/context pack and current
  ledgers, not from inherited chat memory.
- Do not let both old and new manager lanes actively dispatch the same loop.
  Overlapping managers are allowed only during explicit handoff validation.

## Dispatcher Role

Dispatcher is a physical delivery role.

Dispatcher may:

- create/continue lane threads;
- send standard handoffs;
- maintain ledger rows;
- perform low-frequency artifact checks;
- include the latest state/feedback artifact path in handoffs when it changes the next context;
- record Claude lifecycle fields (`claude_session_mode`, `reuse_reason`, `next_expected_use`, `close_or_keep`) for Claude handoffs;
- send execution handoffs directly after a validator-passed merged plan when
  the manager records that the user checkpoint is already resolved by prior user
  participation and there is no strategy drift, plan gap, degraded gate, or risky
  expansion;
- use `read_thread` only for blockers, missed artifact windows, or recovery.

Dispatcher must not plan, execute, review, or arbitrate as a substitute for the owner lane.

## Monitoring Cadence

Manager/dispatcher should use bounded, low-frequency monitoring. Every long-running handoff should declare:

```text
expected_artifacts
check_after
deadline
blocker_signal
heartbeat_artifact when useful
```

Default cadence:

| lane state | normal check | read thread? |
|---|---:|---|
| planning / product discovery | 5-10 min or stated `check_after` | only if artifact/deadline is missed or plan is malformed |
| execution / maker running tests or edits | 10-20 min or stated `check_after` | no while active/progressing; read only if idle/errored with missing artifact, malformed artifact, or explicit blocker signal |
| Claude planning/review call | use Claude policy wait; deep calls at least 5 min | inspect command/output artifacts first |
| review / QA | 5-10 min or stated `check_after` | only after missed artifact window |
| arbitration / repair | 5-10 min; faster only for short repairs | only if decisions or verification artifacts are missing |
| dispatcher bookkeeping | after each handoff or artifact landing | no |

Ordinary execution/review deadlines above 45 minutes require a written reason in the handoff or contract. Do not set 60-75 minute blank waits for normal feature execution or bounded review just to avoid polling; use artifact-first checks and shorter recovery windows instead. For active execution lanes, the deadline is not a hard failure cutoff. If the lane is visibly still working, editing, testing, generating screenshots, or responding with progress, continue low-frequency artifact/status checks and do not interrupt with recovery handoffs merely because elapsed time passed the nominal deadline.

User-visible state signals override the clock. If the user says a lane finished, stalled, produced a bad artifact, or is waiting on a review, immediately check expected artifacts and ledger/worklog state; if artifacts are missing or malformed, perform one recovery read/handoff. Do not ignore the user signal because the old `deadline` has not passed.

Subagent completion notifications are also state signals, not passive background
noise. When a delegated worker/subagent reports completion, immediately run the
same artifact-first validation that a heartbeat would run: check expected files,
required headings, verification summaries, and lifecycle/state feedback. Do not
wait for the next monitor window before deciding whether to update ledger/worklog,
delete or retarget stale automations, or route the next lane.

When the route changes, update or delete stale monitors, reminders, or heartbeat automations that still point at obsolete artifacts, lanes, or deadlines. A stale monitor is a coordination bug: it can restart superseded work or make the manager wait on an artifact that no longer matters.

Use exponential backoff for repeated empty checks: first missed window, then one recovery read/handoff, then widen checks unless the lane reports active progress. If the lane reports or shows active progress, prefer continued quiet monitoring over recovery. High-frequency polling is allowed only during short critical handoffs, interactive user decisions, or known near-complete commands.

If a heartbeat or monitor automation has already been created for the same
artifact paths and owner lane, manager/dispatcher should not keep manually
polling in the same turn. After confirming the automation exists and its prompt is
current, stop and let the heartbeat own the next check. Resume manual action only
on a user signal, automation wakeup, malformed/landed artifact, stale-route
cleanup, or one explicit recovery read/handoff.

When creating a heartbeat attached to the current manager thread, verify the
created automation is actually bound to a real thread id. A persisted
`target_thread_id = "current"` literal is invalid for reliable wakeups: delete or
recreate that heartbeat and record the coordination defect. Do not assume a
monitor is active just because the create call returned success; check the
automation record when the wakeup is important for loop progress.

## Continuous Monitoring

When the user explicitly asks manager/dispatcher to keep a loop moving:

- do not end with a normal final while a required artifact is pending and no blocker has been reached;
- prefer artifact/file checks over frequent thread reads;
- use the lane's `check_after` and `deadline`; if absent, set one before or in the next handoff instead of polling blindly;
- if an artifact is missing beyond the wait window, first check whether the owner lane is active; if active/progressing, keep monitoring without interruption;
- if an artifact is missing beyond the wait window and the owner lane is idle, errored, or not showing progress, perform one recovery check and send a structured refocus handoff;
- route the next handoff when the required artifact lands;
- stop only for a real stop state, a user-requested pause, or a blocker requiring user input.

## Context Rules By Role

| role | context style |
|---|---|
| planning | broad project context, prior artifacts, domain skills, iterative Claude allowed |
| execution | merged plan + local code/tests needed for implementation |
| review | fresh bounded evidence bundle; no inherited planning-Claude context |
| arbitration | both reviews + live evidence + execution report |
| manager/dispatcher | coordination artifacts first; thread reads only for recovery |

## Context Selection

Use role-scoped context as a starting point, not a capability limit:

| lane | default context |
|---|---|
| planning / product | brief, prior final reports, project structure, relevant specs/code, domain skills, Claude planning artifact |
| execution / maker | merged plan, local files/tests for the phase, existing patterns, failing tests |
| review / QA | merged plan, execution report, changed diff, relevant complete functions, test output, acceptance criteria |
| arbitration / repair | both reviews, execution report, targeted live evidence, verification output |
| manager / dispatcher | ledger rows, artifact paths, lane state, deadlines, blockers |

Rules:

- Handoffs should send artifact paths and exact read requirements, not pasted full artifacts, when the artifact already exists.
- Only planning should routinely rebuild broad project context. Other lanes must justify broad reads with a concrete gap.
- Execution phases should be large enough to land a user-visible workflow state, product surface, or stable contract before full dual review.
- Review should not inspect the whole repository by default. Build a bounded evidence bundle from diffs, relevant full functions, tests, and constraints.
- Manager/dispatcher should not consume worker reasoning. It tracks state and routes the next handoff from artifacts.
- If a lane needs more context for quality, correctness, or recovery, it should ask for or read the narrowest missing source first. Expand broader only when the narrow source is insufficient.

## Handoff Requirements

Every cross-lane message should include:

```text
<!-- LOOP:AGENT_MESSAGE v1 -->
message_type
loop_id
message_id
from_lane / to_lane
from_thread / to_thread when known
delivered_by_lane / delivered_by_thread / delivery_reason when physical sender differs
claude_policy
execution_owned_subagents when `to_lane` is execution-agent
source artifacts
task
boundaries
write scope
required output
exit criteria
context_sources
expected_artifacts
check_after
deadline
blocker_signal
claude_lane_id / loop_id / lane_role / lane_scope / reasoning_tier / claude_session_mode / next_expected_use / close_or_keep when Claude is invoked
```

Never send an unstructured "continue" for loop work.

# Claude Policy Reference

Use this reference when a loop handoff, lane artifact, plan, review, or arbitration needs an explicit Claude policy. Keep `not_needed` lightweight; do not turn Claude into ceremony for mechanical work.

## Policy Tiers

| claude_policy | Use When | Required Fields |
|---|---|---|
| `required` | Risky architecture, migrations, auth/data-loss, frontend/backend linkage, process or skill changes that affect future agent behavior, plan/review work with lasting protocol impact, or substantive Codex/Claude disagreement. | `claude_policy`, `claude_mode`, `claude_reason`, `required_claude_artifact`, `fallback_if_claude_unavailable` |
| `conditional` | Claude may help, but current evidence may make it unnecessary: implementation-risk consultation, unclear-plan analysis, review uncertainty, or workflow design pressure checks. | Include `claude_policy`, `claude_mode`, `claude_reason`; if skipped, write `Claude skipped: <reason>`. Add artifact/fallback only when Claude is invoked or actively considered. |
| `not_needed` | Dispatcher delivery, status polling, ledger bookkeeping, manager status lookup, tiny docs/config fixes, or mechanical execution of already-reviewed narrow scope. | Use compact `claude_policy: not_needed` plus a short reason. Do not require mode/artifact/fallback fields unless useful. |

## Required Close-Out Gate

A lane with `claude_policy: required` cannot close out its final lane conclusion, execution report, review, or final report without either the `required_claude_artifact` or a recorded `claude-unavailable: <reason>` with elapsed wait and an explicit block-or-degrade decision. Dispatcher and manager lanes may flag a missing required Claude artifact or gate, but cannot satisfy it for the lane.

When a required Claude artifact is unavailable, malformed, empty, or times out, do not silently continue to the next substantive loop phase. Write the unavailable marker first, then surface a user/manager decision checkpoint before arbitration, repair, or execution proceeds as if dual review happened. The checkpoint should offer concrete choices:

- retry Claude with the same route after a short wait;
- optimize or split the bounded prompt and retry once;
- proceed degraded with Codex-only evidence, explicitly marking the missing Claude review;
- pause the loop until Claude connectivity or prompt strategy is fixed.

Only skip this checkpoint when the handoff already contains an explicit user-approved degraded-continuation rule for that exact phase.

## Lane-Owned Claude

- The lane that needs Claude invokes Claude, saves the Claude artifact or unavailable marker, judges the output with Codex-visible evidence, and writes the lane conclusion.
- Planning lanes may use Claude for independent plans, plan critique, route comparison, and workflow pressure tests.
- Execution lanes may use Claude for read-only implementation-risk consultation or unclear-plan analysis. Claude must not edit files unless the user explicitly asks.
- Review lanes may use Claude for read-only review and evidence-seeking critique.
- Arbitration lanes may use Claude only as evidence or bounded debate input; arbitration decisions cite artifacts, not model identity.
- Dispatcher and manager lanes must not run Claude on behalf of lanes. They may flag missing required Claude artifacts or unavailable markers.

## Claude Session Lifecycle

Do not start a fresh Claude conversation by habit. Choose the session lifecycle from the lane purpose, then record the choice in the handoff, Claude artifact, or ledger.

Required lifecycle fields for substantive Claude use:

```text
claude_session_mode: fresh | reuse | one_shot
claude_lane_id: <named Terminal lane/session id, or "unknown">
reuse_reason: <why this session should continue, or "none">
next_expected_use: <specific next use, or "none">
close_or_keep: close | keep | checkpoint
```

Use `fresh` when independence is part of the quality gate: read-only review, adversarial critique, second opinion, or architecture pressure tests that must not inherit planning or execution bias. Fresh review Claude must receive a bounded evidence bundle; do not reuse a planning/design Claude session for review just because it is already open.

Use `reuse` when continuity is valuable: ongoing strategy, product direction, UX/design critique, route comparison, or iterative planning on the same loop. Before opening a new Claude planning/design lane, manager/dispatcher should check the ledger for an existing reusable Claude companion and continue it unless it is stale, blocked, or polluted by incompatible scope.

Use `one_shot` for smoke tests, narrow bounded checks, simple artifact validation, or a single consultation with no expected follow-up.

Close/archive the Claude lane when `next_expected_use: none`, the artifact says the consultation is complete, or the next phase needs independent review. Keep it only when a concrete next use is named, such as "continue product/design critique after user screenshot feedback." Use `checkpoint` when the user or manager must decide whether continuity still helps.

## Companion Versus Review Routing

Do not use Claude as CI for every batch. Route Claude by the value of continuity
versus independence:

| route | session mode | use for | do not use for |
|---|---|---|---|
| Claude companion lane | `reuse` | strategy, product direction, UX/design critique, route comparison, repeated user calibration, multimodal/manual-style discussion | final independent code review, adversarial quality gates |
| Claude independent review | `fresh` | formal read-only review after a user-visible workflow, stable contract, high-risk change, or user-required dual review | ongoing product/design discussion |
| Claude one-shot | `one_shot` | smoke tests, connectivity checks, narrow validation, single bounded consultation | accumulating project memory |

Default cadence:

- Do not invoke Claude for helper-level fixes, tiny internal patches, routine tests, or
  mechanical follow-ups when Codex review/arbitration is enough.
- Prefer a long-lived companion lane for product/design/strategy because repeated
  context improves judgment and reduces cold-start prompt churn.
- Preserve freshness for formal review because independence is the quality gate.
- If a companion discussion produces a decision, summarize it into a formal artifact
  before execution or arbitration relies on it.
- If formal Claude review is unstable, retry once with a smaller bounded packet
  in a fresh named Terminal lane, then record whether the result is a formal
  review artifact or unavailable. Do not silently treat a companion opinion as
  an independent review.

For Claude review lanes, the default lifecycle is:

```text
claude_session_mode: fresh
next_expected_use: none
close_or_keep: close
```

After the review artifact exists, is non-empty, contains required headings, and is
recorded in the ledger/worklog, archive the lane. Do not leave completed review
lanes open in the sidebar for possible reuse; reuse would undermine independent
review. Product/design Claude companion lanes may be kept only with a concrete
named future use and must never be reused for review.

Session lifecycle does not replace artifact discipline. Reused Claude context is a thinking aid; any decision that other lanes rely on must still be summarized into a formal artifact with source paths and current acceptance criteria.

## Claude By Lane

Planning Claude:

- may use broad project context and iterative discussion;
- may receive richer 10-15 KB bounded prompts or split context packs;
- may continue a planning conversation while the plan is being developed;
- must summarize discussion into a formal plan artifact before merge.

Execution Claude:

- is conditional and read-only by default;
- is used for plan gaps, source-policy uncertainty, or risk-boundary questions;
- must not casually change direction after a merged plan exists.

Review Claude:

- should be a fresh independent session, not a continuation of planning Claude;
- must not read Codex's independent review before both reviews are complete;
- should receive a bounded review bundle containing the merged plan, execution report, changed diffs or complete relevant functions, tests, acceptance criteria, and known constraints;
- may use narrow live-path access only when the bundle is insufficient and the access need is explicit.
- produces an independent review artifact, not a final verdict. Do not require Codex to re-verify every Claude finding immediately inside the Claude review lane; comparison, conflict analysis, and acceptance/rejection belong to arbitration unless a finding is obviously malformed, unsupported by the supplied evidence, or safety-critical.

Arbitration Claude:

- is optional evidence/debate input only;
- does not decide by authority. Arbitration decisions cite artifacts and live evidence.


## Invocation And Waits

- Ordinary Claude Terminal lanes should use the lane's packet size and risk to
  set a bounded wait; deep required planning or review needs a longer hard
  timeout than smoke tests.
- For deep required Claude planning or review calls, wait at least five minutes
  before declaring timeout unless the output/done artifacts appear earlier.
  Record the lane id, packet path, output path, done path, elapsed wait, and
  whether the wait was ordinary or deep required review.
- For ordinary bounded Claude reviews with a 10-35 KB evidence packet, use
  `check_after: 5-8 minutes` and a normal hard deadline around `10-15 minutes`.
  Do not set 30-45 minute deadlines unless the lane explicitly says it is a
  deep review, whole-phase architecture review, or slow external operation.
- Local macOS/Codex Claude calls must use a visible named Terminal lane:

```bash
cd "$PROJECT_ROOT"
claude --name "$CLAUDE_LANE_ID" --permission-mode acceptEdits \
  "Read and execute this packet exactly: $CLAUDE_PACKET"
```

Preferred launcher:

```bash
python3 skills/loop-engineering/scripts/launch-claude-terminal-lane.py \
  --lane-id "$CLAUDE_LANE_ID" \
  --packet "$CLAUDE_PACKET" \
  --cwd "$PROJECT_ROOT"
```

- For a follow-up task in the same reusable companion lane, add `--reuse`.
- For a completed lane with no future use, close it after artifact validation:

```bash
python3 skills/loop-engineering/scripts/launch-claude-terminal-lane.py \
  --lane-id "$CLAUDE_LANE_ID" \
  --close
```

- `acceptEdits` is required when Claude must write output and done artifacts.
  `dontAsk` may let Claude process the packet but can block writes.
- The packet must include:
  - `lane_id`
  - `claude_session_mode`
  - source artifacts / bounded evidence
  - allowed write scope
  - required output artifact path
  - required done JSON path
  - required headings
  - stop condition and fallback instructions
- Codex/dispatcher may launch the lane with Terminal automation and send the
  packet instruction, but it must judge completion from files, not terminal chat.
- A valid Claude lane writes the Markdown output plus a done JSON containing
  `lane_id`, `status: done`, `output`, required-heading status, and any short
  notes. Codex validates both files before accepting the artifact.
- After validation, record `next_expected_use` and `close_or_keep`. Close
  one-shot/fresh review Terminal lanes with no future use; reuse existing
  companion Terminal lanes only when a named future use exists.
- Do not use terminal bridge scripts, direct `claude --bare`, or direct stdin as
  the local macOS/Codex default route. Historical artifacts that mention those
  routes remain historical evidence only.
- Use 10-35 KB bounded packets for formal planning/review when a rich answer is
  needed; split larger surfaces into staged packets.
- Tiny prompts only prove Terminal lane connectivity; do not treat them as
  substantive planning or review.
- For required reviews and deep consultations, Claude should review bounded evidence, not rediscover or rescan the whole repository by default.
- Build the bounded prompt from the smallest useful evidence set: source artifact paths, relevant diffs, key code/test excerpts, command output, failure markers, review priorities, and required headings. Include paths as provenance, but do not rely on Claude reading those paths unless live-path access is explicitly needed.
- Prompt size must be designed for useful judgment, not merely for successful invocation. Avoid both extremes: do not send whole-project context that routinely causes empty, truncated, or malformed Claude output; also do not shrink the prompt by omitting the code paths needed to judge the requested contract. Prefer a medium evidence pack with exact critical functions, exact diffs, focused tests, and verification output.
- Bounded prompts must preserve critical code exactly. Do not replace reviewed logic with ellipses, pseudocode, invented placeholders, rewritten summaries, or truncated return/exception paths when Claude may judge that logic. For any function that could support a finding, include the complete relevant function body or an exact diff hunk with enough surrounding lines to show inputs, branches, side effects, and return values.
- Accuracy beats compactness. If an accurate bounded prompt would be too large, split it into multiple accurate bounded prompts or use a narrow `--add-dir` fallback when justified. If neither is practical, record `review-unavailable` or `partial: insufficient bounded context`; do not send a lossy prompt that is likely to induce false findings.
- For large review surfaces, use staged evidence packs instead of one oversized prompt or one under-specified prompt. A good default split is: contract and execution summary; complete critical production functions; focused tests and verification output; then, only if needed, a follow-up pack for a specific disputed finding. Each pack must be internally truthful and must state what was omitted.
- When a prompt intentionally omits live paths or details, label those omissions explicitly and instruct Claude not to infer beyond the supplied evidence.
- For images, screenshots, PDFs, or other binary/visual inputs, Codex should first extract the visible text, structure, and relevant observations, then pass that bounded representation to Claude. Do not use whole-directory access just to make Claude discover images or scan unrelated files.
- Use live path access only as an exception after the bounded packet shows a
  concrete gap, or when Claude explicitly must inspect files directly. Scope it
  to the narrowest required paths.
- Keep the approval surface narrow: launch named Terminal lanes for Claude, and
  avoid broad shell/interpreter approvals solely for Claude connectivity.
- Validate artifacts before accepting a Claude result. Required review output
  must contain `## Findings`; planning or debate prompts must contain the
  headings requested in the packet. A done JSON without a non-empty validated
  output is not enough.
- If a bounded packet is large or returns malformed output, retry once with a
  smaller packet or stricter output contract before degrading. Record packet
  path, approximate size, lane id, elapsed wait, and why it was accepted or
  degraded.

## Failure Classification

| Symptom | Marker | Next action |
|---|---|---|
| Terminal lane cannot launch | `claude-unavailable: launch-failed` | retry once only if the failure is clearly transient; otherwise checkpoint/degrade |
| output/done files missing past deadline | `claude-unavailable: timeout` or `review-unavailable: timeout` | reduce packet scope or retry once in a fresh named lane |
| done JSON exists but output is empty/missing | `review-unavailable: malformed-output` | do not accept; retry once with stricter packet if useful |
| output exists but missing required headings | `review-unavailable: malformed-output` | do not accept as review evidence |
| done JSON `lane_id` mismatches the expected lane | `review-unavailable: lane-mismatch` | do not accept; inspect lane routing before retry |
| non-empty output, required headings, matching done JSON | usable Claude artifact | record lane id, packet path, output path, done path, and omitted live paths |

For `claude_policy: required`, any unavailable marker from this table is a stop-and-ask condition unless the user already approved degraded continuation for the exact lane. The lane should not convert "Claude failed" into "Codex proceeds normally"; it should ask whether to retry, optimize/split the prompt, proceed degraded, or pause.

## Path Access Fallback

- If Claude cannot read a required live path, the lane that needs Claude first creates a bounded packet with the relevant exact excerpts. Use live-path access only when bounded context is insufficient or Claude explicitly needs file inspection.
- Do not ask Claude to inspect the whole worktree merely for planning, critique, image discussion, or review of already-known artifacts. Codex owns context selection; Claude owns independent judgment over the selected evidence.
- If Claude still cannot access the path, record `partial: <path> unreadable` or `claude-unavailable: <reason>`.
- Codex must verify the live path directly before accepting Claude claims about that path.
- Dispatcher must not summarize or bridge unreadable content for Claude.

## Decision Block

When Claude is used in a lane artifact, include:

```text
Claude said:
Codex accepts:
Codex rejects:
needs evidence:
final lane decision:
```

## Cross-Review Merge Discipline

- Claude review and Codex review are independent inputs. Neither review is authoritative by itself.
- Do not spend a full Codex verification cycle on every Claude finding inside the review lane. Arbitration should merge both review artifacts, group common findings, identify conflicts, and then verify only the findings that affect acceptance, severity, repair scope, or user-visible risk.
- Shared Claude/Codex findings deserve priority, but agreement is not proof. Conflicting findings, high-severity findings, and findings based on partial prompt evidence require live-path or artifact evidence before acceptance.
- A Claude finding that appears caused by prompt omission should be labeled `needs evidence` or rejected in arbitration with the missing context cited. The remedy is to improve future evidence-pack design, not to treat the finding as true or to hide the prompt limitation.
- The merge should preserve review diversity: Claude can surface independent concerns from its bounded evidence, while Codex arbitration checks whether those concerns survive the full merged plan, execution report, tests, and live files.

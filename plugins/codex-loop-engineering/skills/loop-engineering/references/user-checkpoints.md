# User Checkpoints Reference

Use this reference when a loop decision may change project direction, when required Claude is unavailable, or when a Codex-only environment needs independent planning/review.

## Principle

Long-running loops need a few explicit user calibration points. Do not ask for every small choice, but do stop before decisions that can redirect scope, product goals, architecture, source policy, review quality, or degraded-tool mode.

## Must Ask

Create a user checkpoint before proceeding when:

- planning has multiple plausible product directions and the choice affects implementation shape;
- user experience expectations, success criteria, or "what good looks like" are underspecified;
- the brief, product goal, or user-facing success criterion changes;
- the merged plan cannot satisfy the brief and a `plan-gap` is written;
- a required Claude planning or review artifact is missing, empty, malformed, or timed out;
- the loop would proceed degraded after a required dual-model gate;
- review or arbitration would change scope, data contract, architecture, source policy, or phase boundary;
- a frontend/product preview is technically valid but the user says it does not match the intended visual direction, workflow feel, or "what good looks like";
- user correction would supersede an active execution, review, arbitration, monitor, or expected artifact path;
- two independent reviews agree on a P0 and arbitration cannot disprove it with strong evidence;
- the manager detects context drift between the original brief and current lane output;
- a lane wants to replace a formal artifact with chat memory or a summary.

Do not continue to execution, repair, or final report through these gates unless the user has explicitly approved that exact degraded path or direction change.

## Should Usually Not Ask

Avoid interrupting the user for:

- ordinary implementation defects inside the merged plan;
- test additions for planned behavior;
- formatting or documentation edits inside accepted scope;
- choosing a smaller safe repair in arbitration via `third path`;
- routine retries within the recorded Claude policy wait/retry rules.

## Checkpoint Shape

Keep checkpoint prompts short and decision-oriented:

```text
Checkpoint: <decision name>
Why it matters: <one sentence>
Current evidence: <artifact paths / failure marker>
Options:
1. Retry / gather more evidence
2. Proceed degraded with explicit marker
3. Return to planning / revise brief
4. Pause
Recommended: <one option + reason>
```

When the UI supports a decision popup, use it for these checkpoints. When it does not, ask inline with the same structure and do not continue until the user chooses, unless the handoff already contains a specific auto-resolution rule.

## Planning Calibration

Planning checkpoints should happen before a merged plan becomes executable when user intent is ambiguous. Keep them sparse and high leverage:

- ask about product direction, workflow feel, priority tradeoffs, and acceptance criteria;
- present 2-3 concrete choices and one recommended option;
- write the user's answer into the brief, merged plan, or decision log;
- do not ask the user to decide internal helper structure unless it changes workflow, risk, or maintainability;
- if the user rejects the generated plan's direction, revise the plan artifact before execution instead of relying on chat correction.

Example planning checkpoint:

```text
Checkpoint: Phase 3 workflow shape
Why it matters: This decides whether execution optimizes for one complete user loop or several small command slices.
Options:
1. One larger user loop: guide + acquisition refresh + queue lifecycle + weekly/publication readiness.
2. Two medium loops: daily/queue first, weekly/PPT second.
3. Small slices: command center first, then each runner separately.
Recommended: option 2, because it improves speed without hiding too much risk.
```

## Preview Calibration

For frontend or product-surface work, the preview checkpoint is an acceptance gate, not a courtesy update. Offer a small set of actions:

1. Accept the visible direction and proceed to review or backend continuation.
2. Revise the visible shape before deeper wiring.
3. Run a bounded design critique over the screenshot and touched files.
4. Pause.

If the user rejects the preview, update the relevant plan/contract or write a superseding decision artifact before more implementation. Do not rely on chat correction alone.

## Claude-Unavailable Planning

If Claude planning is required but unavailable:

1. Write `claude-unavailable: <reason>` in the Claude plan artifact path or an adjacent marker.
2. Stop at a user checkpoint before merging.
3. Offer:
   - retry Claude;
   - split/optimize the prompt and retry once;
   - proceed Codex-only with two independent Codex planning subagents or isolated contexts;
   - pause until Claude is fixed.

Do not fabricate `10-plan-claude.md` from Codex's own plan.

## Codex-Only Independent Planning

When the user has no Claude or approves Codex-only mode:

- keep the artifact structure explicit, but rename sources honestly, for example `10-plan-codex-independent-a.md` and `11-plan-codex-independent-b.md`;
- launch independent Codex subagents when subagent tooling is available. Use different prompts or roles, such as product/planning and architecture/risk;
- if subagent tooling is unavailable, use separate isolated Codex contexts/threads and record `subagent-unavailable: <reason>`;
- prevent cross-contamination: the second planning pass must not read the first before both artifacts exist;
- merge them with the same conflict-resolution discipline used for Claude/Codex plans;
- mark the merged plan `review_mode: codex_only_independent` or equivalent.

Codex-only mode is valid, but it is a degraded/capability-different path when the brief asked for Claude. Be honest in artifacts.

## Codex-Only Independent Review

When Claude review is unavailable or not configured:

- launch independent Codex subagent reviewer(s) when subagent tooling is available;
- produce two independent Codex review artifacts from subagents or isolated contexts when possible;
- neither review reads the other before arbitration;
- use the same bounded evidence bundle standards as Claude review;
- arbitration merges findings by evidence, not by reviewer identity;
- final report records `review_mode: codex_only_independent` and the reason Claude was not used.

Do not call a single current-thread self-review an independent review. If only the current thread is available, mark `independent-review-unavailable` and ask the user whether to proceed degraded.

## Drift Control

At each major phase boundary, manager/arbitration should compare:

- original brief / user constraints;
- merged plan;
- execution report;
- review findings;
- proposed next action.

If the proposed next action changes the project direction instead of completing the accepted phase, stop for a checkpoint.

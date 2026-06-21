# Strategic Loop Contract

Use this reference when a T3/T4 loop needs a strategic target that can be dispatched, checked, and stopped. This replaces a separate `/loop contract`: the strategic document and the operational contract should be one artifact, not two competing files.

## When Required

Create or update a Strategic Loop Contract before execution when:

- route tier is T3 or T4;
- the work changes product direction, architecture, workflow boundaries, or cross-lane coordination;
- the user asks for a manager/dispatcher loop that should keep moving;
- a prior plan lacks a clear "good enough" target or stop condition.

For T0/T1/T2, use the fields lightly in the current thread or checklist. Do not create heavyweight documents for small work.

## Contract Shape

```yaml
strategy:
  loop_id:
  goal:
  end_state:
  good_enough:
  non_goals:
  user_value:
  evidence_of_success:
  stop_condition:
  user_checkpoints:

operation:
  route_tier: T0|T1|T2|T3|T4|T5
  route_justification:
  six_interfaces:
    goal:
    state:
    context:
    act:
    capture:
    stop:
  lanes:
    - name:
      role:
      decision_rights:
      write_scope:
      output_artifact:
  state_sources:
  context_pack:
  allowed_actions:
  capture_required:
  expected_artifacts:
  claude_policy:
  required_claude_artifact:
  fallback_if_claude_unavailable:
  check_after:
  deadline:
  blocker_signal:
```

## Rules

- `strategy.good_enough` is mandatory for T3/T4. If absent, write `strategy-gap: missing good_enough` and stop before tactical or execution planning.
- `operation.route_tier` must be chosen before lanes are created.
- T3/T4 execution batches must be product-surface, workflow-state, durable-contract, migration, source-policy, or security slices. Do not make helper-level batches full review units.
- `state_sources` should point to ledgers, worklogs, prior final reports, specs, or durable state files. Chat history alone is not state.
- `capture_required` must name what evidence will be written: command output, diff, screenshot, review finding, artifact path, or decision log.
- `stop_condition` must include done evidence and hard stops such as user checkpoint, max rounds, budget cap, no new evidence, production/destructive risk, or route-tier mismatch.
- `check_after` and `deadline` must match the lane type. Ordinary bounded reviews usually need a 5-8 minute first check and a 10-15 minute deadline; ordinary execution should not have a 60-75 minute blank window unless long tests, deep review, or external tools justify it. For execution lanes, `deadline` is a recovery threshold for idle/errored/no-progress states, not a hard failure cutoff while the lane is visibly active and making progress.
- `blocker_signal` must include user-visible completion/blocker corrections when the manager is actively monitoring. A user saying "this lane is done" or "the review is missing" is a state signal that triggers immediate artifact-first checking.
- Frontend/product-surface execution contracts must describe the visible UI shape and user calibration point, including placeholder/degraded states when backend behavior is deferred.

## Dispatch Use

Manager/dispatcher should send artifact paths and exact read requirements from the contract. Do not paste the whole contract into every handoff when the artifact exists.

Execution lanes read the merged plan and the contract. Review lanes read the contract, execution report, changed diff, tests, and relevant complete functions. Arbitration reads the contract, reviews, execution report, and live evidence.

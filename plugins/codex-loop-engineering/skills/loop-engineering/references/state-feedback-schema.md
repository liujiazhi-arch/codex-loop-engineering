# State And Feedback Schema

Use this reference when a loop has multiple rounds, lanes, reviews, repairs, or user checkpoints. The goal is to make `capture -> feedback -> state -> next context` explicit so the next agent does not rediscover the same facts from chat.

## Core Rule

Every meaningful loop event should answer:

```text
What changed?
What evidence proves it?
How does the next prompt, plan, or action change?
Who owns the next step?
Should the loop stop or continue?
```

## State Event

Append state events to a worklog, ledger, or dedicated state artifact.

```yaml
state_event:
  loop_id:
  event_id:
  created_at:
  phase:
  owner_lane:
  status: pending|active|blocked|completed|deferred
  latest_artifacts:
  accepted_decisions:
  open_blockers:
  user_decisions:
  next_owner:
  next_action:
  stop_or_continue:
  evidence:
```

## Feedback Event

Use feedback events after review, arbitration, repair, failed validation, missed artifact windows, or user corrections.

```yaml
feedback_event:
  loop_id:
  source_event:
  source_lane:
  finding:
  evidence:
  decision: accept|reject|third_path|defer|needs_more_evidence|checkpoint
  next_prompt_delta:
  next_context_delta:
  next_action:
  next_owner:
  stop_or_continue:
```

## Communication Rules

- Do not store hidden chain-of-thought. Store decisions, evidence, artifacts, and prompt/context deltas.
- A review finding is not feedback until it changes a decision, next prompt, next context, or next action.
- Arbitration must convert accepted review findings into feedback events or explain why no next-context change is needed.
- Manager/dispatcher should read state/feedback artifacts before reading worker chat.
- If an event changes scope, product direction, architecture, data contract, source policy, or degraded-tool mode, mark `stop_or_continue: checkpoint`.
- If the same failure repeats and `next_prompt_delta` is empty, stop for a planning or user checkpoint instead of looping.
- If an event supersedes an active artifact, lane route, monitor, or expected output, record what is now historical, what replaces it, and which stale checks must be updated or deleted.
- If the user correction changes the strategic target, execution boundary, or "good enough" definition, update or append the Strategic Loop Contract and rerun its validator before dispatching the next production execution lane.

## Superseding Event

Use this compact form when a user correction, planning decision, or failed preview invalidates an older route:

```yaml
superseding_event:
  loop_id:
  created_at:
  supersedes:
    artifacts:
    lanes:
    monitors:
  reason:
  replacement_artifacts:
  new_owner:
  next_action:
  validator_required: true|false
  stop_or_continue: checkpoint|continue
```

## Minimal Inline Form

For small loops, a compact markdown entry is enough:

```markdown
State:
- phase:
- status:
- latest artifacts:
- blockers:
- next owner:

Feedback:
- finding:
- evidence:
- decision:
- next prompt/context change:
- next action:
- stop/continue:
```

# Codex Loop Engineering

Codex Loop Engineering is a Codex plugin for substantial work that benefits from explicit planning, execution, review, arbitration, and repair loops.

Use it when a single pass is likely to miss edge cases: deep refactors, large feature work, architecture-affecting fixes, research synthesis, product/design workflows, multi-file migrations, or recurring processes that need artifact-backed coordination.

## What It Provides

- Route tiers from direct current-thread work to full multi-lane loops.
- A six-interface contract: goal, state, context, act, capture, and stop.
- Artifact protocols for briefs, plans, execution reports, reviews, arbitration, and final reports.
- Claude/Codex review guidance with honest Codex-only fallback paths when Claude is unavailable.
- State and feedback schemas so future agents do not rediscover the same facts from chat history.
- Helper scripts for launching visible Claude Terminal lanes and validating Strategic Loop Contracts.

## Install

Clone the repository, then add it as a local Codex plugin source according to your Codex plugin workflow.

```bash
git clone https://github.com/liujiazhi-arch/codex-loop-engineering.git
```

For local development in the Codex desktop app, you can also keep the repository under a local marketplace or personal plugin directory and install `codex-loop-engineering` from there.

## Quick Start

Ask Codex to use the skill:

```text
Use Codex Loop Engineering for this refactor.
```

Typical artifact bundle:

```text
docs/loop-engineering/YYYY-MM-DD-slug/
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

For smaller tasks, the skill should downgrade to a checklist or direct current-thread work instead of creating unnecessary lanes.

## Requirements

- Codex with plugin and skill support.
- Python 3 for bundled helper scripts.
- Optional: Claude CLI if you want Claude planning or review lanes. The skill includes Codex-only independent planning/review fallback guidance when Claude is not available.
- Optional on macOS: Terminal automation for visible named Claude lanes.

## Helper Scripts

Validate a Strategic Loop Contract:

```bash
python3 skills/loop-engineering/scripts/validate-loop-contract.py <contract-or-merged-plan.md>
```

Preview a Claude Terminal lane command without launching it:

```bash
python3 skills/loop-engineering/scripts/launch-claude-terminal-lane.py \
  --lane-id review-lane \
  --packet path/to/packet.md \
  --cwd "$PWD" \
  --dry-run
```

## Privacy

This plugin does not include API keys, private endpoints, or third-party gateway code. It is a workflow plugin; generated project artifacts may contain sensitive project details, so review artifacts before sharing them publicly.

## License

MIT. See [LICENSE](LICENSE).

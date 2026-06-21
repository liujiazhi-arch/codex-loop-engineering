# Contributing

Thanks for improving Codex Loop Engineering.

## Scope

This plugin should stay focused on Codex-centered loop orchestration:

- route tiers;
- artifact-first planning and handoffs;
- independent review and arbitration;
- repair loops;
- state, feedback, and stop rules;
- helper scripts that make those workflows more reliable.

Avoid adding unrelated general coding workflows unless they directly support loop orchestration.

## Before Opening A Pull Request

Run:

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
python3 /path/to/skill-creator/scripts/quick_validate.py skills/loop-engineering
python3 -m py_compile skills/loop-engineering/scripts/*.py
```

Also scan for private paths, credentials, and project-specific examples before publishing.

## Skill Changes

For changes to `skills/loop-engineering/SKILL.md` or `references/`, include:

- the problem the change solves;
- the route tier, lane, or artifact protocol affected;
- any forward-test prompt or scenario used;
- validation command output.

Keep `SKILL.md` concise. Put detailed optional guidance in `references/` and link to it from the main skill.

## Scripts

Helper scripts should be deterministic, local-first, and safe to run without secrets. Include a dry-run mode when a script would otherwise launch external tools.

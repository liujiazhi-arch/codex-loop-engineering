#!/usr/bin/env python3
"""Lightweight checker for loop-engineering Strategic Loop Contracts.

This is a guardrail, not a full parser. It checks for fields that are easy to
forget before dispatching T2+ / T3+ loop work.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


TIER_ORDER = {"t0": 0, "t1": 1, "t2": 2, "t3": 3, "t4": 4, "t5": 5}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower())


def has_any(norm: str, needles: list[str]) -> bool:
    return any(normalize(needle) in norm for needle in needles)


def has_gap_marker(text: str, marker: str) -> bool:
    pattern = rf"(?im)^\s*(?:[-*]\s*)?{re.escape(marker)}\s*:"
    return re.search(pattern, text) is not None


def detect_tier(text: str) -> str | None:
    patterns = [
        r"\broute[_ -]?tier\s*[:=]\s*(T[0-5])\b",
        r"\broute tier\b[^T]*(T[0-5])\b",
        r"\b(T[0-5])\s*\|\s*",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).lower()
    return None


def validate(text: str) -> dict[str, object]:
    norm = normalize(text)
    tier = detect_tier(text)
    tier_rank = TIER_ORDER.get(tier or "", -1)
    errors: list[str] = []
    warnings: list[str] = []

    if not tier:
        errors.append("missing route_tier")

    if tier_rank >= 2:
        for field in ["goal", "state", "context", "act", "capture", "stop"]:
            if not has_any(norm, [field]):
                errors.append(f"missing six-interface field: {field}")

        if not has_any(norm, ["done check", "done_check", "stop condition", "stop_condition"]):
            errors.append("missing done/stop condition")

    if tier_rank >= 3:
        for field in ["good_enough", "good enough"]:
            if has_any(norm, [field]):
                break
        else:
            errors.append("missing strategic good_enough target")

        if not has_any(norm, ["expected_artifacts", "expected artifacts"]):
            errors.append("missing expected_artifacts")
        if not has_any(norm, ["check_after", "check after"]):
            errors.append("missing check_after")
        if not has_any(norm, ["deadline"]):
            errors.append("missing deadline")
        if not has_any(norm, ["blocker_signal", "blocker signal"]):
            warnings.append("missing blocker_signal")

    if has_any(norm, ["claude_policy_required", "claude policy required", "claude_policy_required"]):
        if not has_any(norm, ["required_claude_artifact", "required claude artifact"]):
            errors.append("claude_policy required but missing required_claude_artifact")
        if not has_any(norm, ["fallback_if_claude_unavailable", "fallback if claude unavailable"]):
            errors.append("claude_policy required but missing fallback_if_claude_unavailable")

    if has_gap_marker(text, "strategy-gap") or has_gap_marker(text, "strategy_gap"):
        warnings.append("strategy-gap marker present; execution should not start")
    if has_gap_marker(text, "plan-gap") or has_gap_marker(text, "plan_gap"):
        warnings.append("plan-gap marker present; execution should not start")

    return {
        "route_tier": tier.upper() if tier else None,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a loop-engineering Strategic Loop Contract.")
    parser.add_argument("path", help="Contract, handoff, or merged plan file to validate")
    parser.add_argument("--json", action="store_true", help="Emit JSON result")
    args = parser.parse_args()

    path = Path(args.path)
    text = path.read_text(encoding="utf-8")
    result = validate(text)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "OK" if result["ok"] else "FAIL"
        print(f"{status}: {path}")
        print(f"route_tier: {result['route_tier']}")
        for err in result["errors"]:
            print(f"ERROR: {err}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

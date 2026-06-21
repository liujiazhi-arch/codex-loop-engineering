#!/usr/bin/env python3
"""Launch a visible named Claude Terminal lane.

The lane must write its own output artifact and done JSON as instructed by the
packet. Codex should validate those files instead of scraping terminal chat.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_REGISTRY = Path(
    os.environ.get("CLAUDE_TERMINAL_LANE_REGISTRY", "/private/tmp/loop-engineering-claude-terminal-lanes.json")
)
TERMINAL_APP = 'application "Terminal"'
REF_SEPARATOR = "|||"
PERSISTENT_COMPANION_ROLES = {"planning-companion", "product-design-companion", "strategy-companion"}
ONE_SHOT_ROLES = {"review", "adversarial-review", "second-opinion", "one-shot", "arbitration-consult"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a named Claude Terminal lane.")
    parser.add_argument("--lane-id", help="Claude lane/session name.")
    parser.add_argument("--loop-id", help="Stable loop/project id that owns this Claude lane.")
    parser.add_argument("--lane-role", help="Role family, for example product-design-companion or review.")
    parser.add_argument(
        "--lane-scope",
        help="Stable topic/workstream scope inside the loop, for example ide-ui-density or batch6a-formal-review.",
    )
    parser.add_argument(
        "--session-mode",
        choices=["fresh", "reuse", "one_shot"],
        help="Claude lifecycle mode. Required for launches.",
    )
    parser.add_argument("--next-expected-use", help='Specific future use, or "none". Required for launches.')
    parser.add_argument(
        "--close-or-keep",
        choices=["close", "keep", "checkpoint"],
        help="Lifecycle decision after artifact validation. Required for launches.",
    )
    parser.add_argument(
        "--reasoning-tier",
        choices=["high", "ultra-high"],
        default="high",
        help="Default to high; use ultra-high only for strategy, arbitration, or major UX judgment.",
    )
    parser.add_argument("--packet", type=Path, help="Packet path Claude should execute. Required unless --close is used.")
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="Project working directory.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY, help="Claude lane registry JSON path.")
    parser.add_argument(
        "--permission-mode",
        default="bypassPermissions",
        choices=["acceptEdits", "dontAsk", "default", "plan", "auto", "bypassPermissions"],
        help="Default to bypassPermissions; override only when a lane must stay constrained.",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="If a Terminal window/tab with this lane id exists, send the packet there instead of opening a new lane.",
    )
    parser.add_argument(
        "--reuse-mode",
        default="interactive",
        choices=["interactive", "shell-command"],
        help="interactive sends only the packet instruction to a live Claude lane; shell-command reruns claude.",
    )
    parser.add_argument(
        "--close",
        action="store_true",
        help="Close Terminal windows whose title contains this lane id, then exit.",
    )
    parser.add_argument(
        "--adopt",
        action="store_true",
        help="Register an already-open named Claude Terminal lane without sending a packet.",
    )
    parser.add_argument("--list", action="store_true", help="Print registry entries and visible Terminal window names.")
    parser.add_argument("--status", action="store_true", help="Print registry/window status for --lane-id.")
    parser.add_argument("--dry-run", action="store_true", help="Print command without launching Terminal.")
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def osascript(script: str) -> str:
    completed = subprocess.run(["osascript", "-e", script], text=True, capture_output=True)
    if completed.returncode != 0:
        time.sleep(0.35)
        completed = subprocess.run(["osascript", "-e", script], text=True, capture_output=True)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "no osascript output").strip()
        raise SystemExit(f"osascript failed: {detail}")
    return completed.stdout.strip()


def applescript_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def terminal_windows() -> list[str]:
    script = f"tell {TERMINAL_APP} to get name of every window"
    output = osascript(script)
    return [name.strip() for name in output.split(", ") if name.strip()]


def terminal_windows_with_warning() -> tuple[list[str], str | None]:
    try:
        return terminal_windows(), None
    except SystemExit as exc:
        return [], str(exc)


def load_registry(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"registry is malformed: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"registry must be a JSON object: {path}")
    return {str(key): value for key, value in payload.items() if isinstance(value, dict)}


def save_registry(path: Path, registry: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def lane_window_markers(lane_id: str) -> tuple[str, str]:
    return (f"--name {lane_id} ", f"--name '{lane_id}' ")


def lane_text_matches(text: str, lane_id: str) -> bool:
    return lane_id in text or any(marker in text for marker in lane_window_markers(lane_id))


def lane_window_matches(window_name: str, lane_id: str) -> bool:
    return lane_text_matches(window_name, lane_id)


def applescript_list(values: list[str]) -> str:
    return "{" + ", ".join(applescript_string(str(value)) for value in values if str(value).strip()) + "}"


def registry_values(entry: dict[str, object], *keys: str) -> list[str]:
    values: list[str] = []
    for key in keys:
        raw = entry.get(key)
        if isinstance(raw, list):
            values.extend(str(value).strip() for value in raw if str(value).strip())
        elif isinstance(raw, str):
            values.extend(value.strip() for value in raw.split(",") if value.strip())
    return sorted(set(values))


def matching_lane_refs(lane_id: str, entry: dict[str, object] | None = None) -> list[dict[str, str]]:
    entry = entry or {}
    marker_a, marker_b = lane_window_markers(lane_id)
    recorded_window_ids = applescript_list(registry_values(entry, "terminal_window_ids", "window_ids"))
    recorded_ttys = applescript_list(registry_values(entry, "terminal_ttys", "interrupted_ttys"))
    script = f"""
tell {TERMINAL_APP}
  set refText to ""
  set recordedWindowIds to {recorded_window_ids}
  set recordedTtys to {recorded_ttys}
  repeat with i from (count of windows) to 1 by -1
    set w to window i
    set winId to (id of w as text)
    set winName to (name of w as text)
    set tabTty to ""
    set tabTitle to ""
    set tabHistory to ""
    try
      set tabTty to (tty of selected tab of w as text)
    end try
    try
      set tabTitle to (custom title of selected tab of w as text)
    end try
    try
      set tabHistory to (history of selected tab of w as text)
    end try
    if (winName contains {applescript_string(marker_a)}) or (winName contains {applescript_string(marker_b)}) or (tabTitle contains {applescript_string(lane_id)}) or (tabHistory contains {applescript_string(lane_id)}) or (winId is in recordedWindowIds) or (tabTty is in recordedTtys) then
      set refText to refText & winId & {applescript_string(REF_SEPARATOR)} & tabTty & {applescript_string(REF_SEPARATOR)} & winName & linefeed
    end if
  end repeat
  return refText
end tell
"""
    output = osascript(script)
    refs: list[dict[str, str]] = []
    for line in output.splitlines():
        parts = line.split(REF_SEPARATOR, 2)
        if len(parts) == 3:
            refs.append({"window_id": parts[0].strip(), "tty": parts[1].strip(), "name": parts[2].strip()})
    return refs


def capture_lane_refs(lane_id: str, entry: dict[str, object] | None = None, *, timeout: float = 2.0) -> list[dict[str, str]]:
    deadline = time.time() + timeout
    refs = matching_lane_refs(lane_id, entry)
    while not refs and time.time() < deadline:
        time.sleep(0.1)
        refs = matching_lane_refs(lane_id, entry)
    return refs


def describe_lane_refs(refs: list[dict[str, str]]) -> list[str]:
    return [f"id={ref.get('window_id', '')} tty={ref.get('tty', '')} name={ref.get('name', '')}" for ref in refs]


def visible_lane_windows(lane_id: str, entry: dict[str, object] | None = None) -> list[str]:
    return describe_lane_refs(matching_lane_refs(lane_id, entry))


def visible_lane_windows_with_warning(lane_id: str, entry: dict[str, object] | None = None) -> tuple[list[str], str | None]:
    try:
        return visible_lane_windows(lane_id, entry), None
    except SystemExit as exc:
        return [], str(exc)


def matching_lane_ttys(lane_id: str, entry: dict[str, object] | None = None) -> list[str]:
    refs = matching_lane_refs(lane_id, entry)
    return sorted({ref["tty"] for ref in refs if ref.get("tty")})


def normalize_tty(tty: str) -> str:
    tty = tty.strip()
    if tty.startswith("/dev/"):
        return tty.removeprefix("/dev/")
    return tty


def live_lane_processes(lane_id: str, ttys: list[str]) -> list[dict[str, str]]:
    normalized = {normalize_tty(tty) for tty in ttys}
    if not normalized:
        return []
    completed = subprocess.run(
        ["ps", "ax", "-o", "pid=,tty=,stat=,command="],
        text=True,
        capture_output=True,
        check=False,
    )
    live: list[dict[str, str]] = []
    for line in completed.stdout.splitlines():
        parts = line.strip().split(None, 3)
        if len(parts) < 4:
            continue
        pid, tty, stat, command = parts
        if tty not in normalized:
            continue
        if lane_id in command or "claude" in command or "caffeinate" in command:
            live.append({"pid": pid, "tty": tty, "stat": stat, "command": command})
    return live


def wait_for_no_live_lane_processes(lane_id: str, ttys: list[str], *, timeout: float = 2.0) -> list[dict[str, str]]:
    deadline = time.time() + timeout
    live = live_lane_processes(lane_id, ttys)
    while live and time.time() < deadline:
        time.sleep(0.1)
        live = live_lane_processes(lane_id, ttys)
    return live


def interrupt_ttys(ttys: list[str], *, lane_id: str) -> list[dict[str, str]]:
    normalized_ttys = [normalize_tty(tty) for tty in ttys]
    for tty in normalized_ttys:
        subprocess.run(["/usr/bin/pkill", "-INT", "-t", tty], check=False)
    if ttys:
        time.sleep(0.8)
    live = wait_for_no_live_lane_processes(lane_id, normalized_ttys, timeout=1.5)
    if not live:
        return []
    for proc in live:
        subprocess.run(["/bin/kill", "-TERM", proc["pid"]], check=False)
    live = wait_for_no_live_lane_processes(lane_id, normalized_ttys, timeout=1.5)
    if not live:
        return []
    for proc in live:
        subprocess.run(["/bin/kill", "-KILL", proc["pid"]], check=False)
    return wait_for_no_live_lane_processes(lane_id, normalized_ttys, timeout=1.5)


def close_lane(lane_id: str, registry_path: Path, *, dry_run: bool) -> int:
    registry = load_registry(registry_path)
    entry = registry.get(lane_id, {"lane_id": lane_id})
    marker_a, marker_b = lane_window_markers(lane_id)
    recorded_window_ids = applescript_list(registry_values(entry, "terminal_window_ids", "window_ids"))
    recorded_ttys = applescript_list(registry_values(entry, "terminal_ttys", "interrupted_ttys"))
    script = f"""
tell {TERMINAL_APP}
  set closedCount to 0
  set recordedWindowIds to {recorded_window_ids}
  set recordedTtys to {recorded_ttys}
  repeat with i from (count of windows) to 1 by -1
    set w to window i
    set winId to (id of w as text)
    set winName to (name of w as text)
    set tabTty to ""
    set tabTitle to ""
    set tabHistory to ""
    try
      set tabTty to (tty of selected tab of w as text)
    end try
    try
      set tabTitle to (custom title of selected tab of w as text)
    end try
    try
      set tabHistory to (history of selected tab of w as text)
    end try
    if (winName contains {applescript_string(marker_a)}) or (winName contains {applescript_string(marker_b)}) or (tabTitle contains {applescript_string(lane_id)}) or (tabHistory contains {applescript_string(lane_id)}) or (winId is in recordedWindowIds) or (tabTty is in recordedTtys) then
      close w saving no
      set closedCount to closedCount + 1
    end if
  end repeat
  return closedCount
end tell
"""
    if dry_run:
        print("Would interrupt matching lane TTY processes before close.")
        print(script.strip())
        return 0
    ttys = matching_lane_ttys(lane_id, entry)
    live_after_interrupt = interrupt_ttys(ttys, lane_id=lane_id)
    if live_after_interrupt:
        entry.update(
            {
                "lane_id": lane_id,
                "status": "close_failed",
                "close_or_keep": "close",
                "next_expected_use": "none",
                "closed_windows": "0",
                "interrupted_ttys": ttys,
                "live_processes_after_interrupt": live_after_interrupt,
                "updated_at": now_iso(),
            }
        )
        registry[lane_id] = entry
        save_registry(registry_path, registry)
        print(json.dumps(entry, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    closed = osascript(script)
    remaining_windows = visible_lane_windows(lane_id, entry)
    status = "closed" if not remaining_windows else "close_failed"
    entry.update(
        {
            "lane_id": lane_id,
            "status": status,
            "close_or_keep": "close",
            "next_expected_use": "none",
            "closed_windows": closed or "0",
            "interrupted_ttys": ttys,
            "remaining_windows": remaining_windows,
            "updated_at": now_iso(),
        }
    )
    registry[lane_id] = entry
    save_registry(registry_path, registry)
    if status != "closed":
        print(json.dumps(entry, ensure_ascii=False, indent=2, sort_keys=True))
        return 2
    return 0


def send_to_existing_lane(lane_id: str, text: str, *, dry_run: bool) -> int:
    marker_a, marker_b = lane_window_markers(lane_id)
    script = f"""
tell {TERMINAL_APP}
  repeat with w in windows
    if (name of w contains {applescript_string(marker_a)}) or (name of w contains {applescript_string(marker_b)}) then
      set index of w to 1
      activate
      do script {applescript_string(text)} in selected tab of w
      return
    end if
  end repeat
  error "Claude lane not found: {lane_id}"
end tell
"""
    if dry_run:
        print(script.strip())
        return 0
    osascript(script)
    return 0


def validate_lifecycle(args: argparse.Namespace) -> None:
    missing = [
        name
        for name in (
            "loop_id",
            "lane_role",
            "lane_scope",
            "session_mode",
            "reasoning_tier",
            "next_expected_use",
            "close_or_keep",
        )
        if getattr(args, name) in (None, "")
    ]
    if missing:
        raise SystemExit("missing Claude lane lifecycle fields: " + ", ".join(missing))
    if is_persistent_companion_role(args.lane_role):
        if args.session_mode != "reuse":
            raise SystemExit(
                "planning/product/design companion lanes must use --session-mode reuse; "
                "use lane_role=one-shot for a disposable Claude consultation"
            )
        if args.close_or_keep == "close" or args.next_expected_use == "none":
            raise SystemExit(
                "planning/product/design companion lanes require a concrete future use "
                "and --close-or-keep keep|checkpoint; use lane_role=one-shot when there is no future use"
            )
    if args.close_or_keep == "close" and args.next_expected_use != "none":
        raise SystemExit('close_or_keep=close requires --next-expected-use "none"')
    if args.close_or_keep in {"keep", "checkpoint"} and args.next_expected_use == "none":
        raise SystemExit("kept Claude lanes require a concrete --next-expected-use")
    if args.session_mode in {"fresh", "one_shot"} and args.reuse:
        raise SystemExit("--reuse is only allowed with --session-mode reuse")
    if args.session_mode in {"fresh", "one_shot"} and args.close_or_keep != "close":
        raise SystemExit("fresh/one_shot Claude lanes must close after artifact validation")
    if args.session_mode == "one_shot" and args.reasoning_tier != "high":
        raise SystemExit("one_shot Claude lanes must use reasoning_tier=high")
    lane_id = getattr(args, "lane_id", "") or ""
    if args.session_mode == "one_shot" and lane_id.startswith("claude-planning-"):
        raise SystemExit(
            "claude-planning-* lanes are planning/product companions; use --session-mode reuse "
            "with a stable companion scope, or choose a non-planning lane id for a true one-shot consultation"
        )


def is_persistent_companion_role(lane_role: str) -> bool:
    return lane_role in PERSISTENT_COMPANION_ROLES or lane_role.endswith("-companion")


def route_key(*, cwd: Path | str, loop_id: str, lane_role: str, lane_scope: str) -> str:
    return f"{cwd}::{loop_id}::{lane_role}::{lane_scope}"


def matching_open_registry_entries(
    registry: dict[str, dict[str, str]], *, cwd: Path, loop_id: str, lane_role: str, lane_scope: str
) -> list[dict[str, str]]:
    cwd_text = str(cwd)
    key = route_key(cwd=cwd_text, loop_id=loop_id, lane_role=lane_role, lane_scope=lane_scope)
    return [
        entry
        for entry in registry.values()
        if entry.get("route_key") == key
        and entry.get("status") == "open"
        and entry.get("close_or_keep") in {"keep", "checkpoint"}
    ]


def validate_lane_id_route(registry: dict[str, dict[str, str]], args: argparse.Namespace) -> None:
    existing = registry.get(args.lane_id)
    if not existing or existing.get("status") == "closed":
        return
    expected = route_key(cwd=args.cwd, loop_id=args.loop_id, lane_role=args.lane_role, lane_scope=args.lane_scope)
    existing_key = existing.get("route_key")
    if existing_key and existing_key != expected:
        raise SystemExit(
            "lane id belongs to a different Claude route: "
            f"{existing_key}; requested {expected}. Choose the existing route or a new lane id."
        )


def print_status(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    windows, warning = terminal_windows_with_warning()
    payload = {
        "registry": registry,
        "terminal_windows": windows,
    }
    if warning:
        payload["terminal_windows_warning"] = warning
    if args.lane_id:
        lane_entry = registry.get(args.lane_id)
        payload["lane"] = lane_entry
        payload["matching_windows"] = visible_lane_windows(args.lane_id, lane_entry)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def record_launch(args: argparse.Namespace, *, action: str) -> None:
    registry = load_registry(args.registry)
    refs = capture_lane_refs(args.lane_id)
    registry[args.lane_id] = {
        "lane_id": args.lane_id,
        "loop_id": args.loop_id,
        "lane_role": args.lane_role,
        "lane_scope": args.lane_scope,
        "route_key": route_key(
            cwd=args.cwd,
            loop_id=args.loop_id,
            lane_role=args.lane_role,
            lane_scope=args.lane_scope,
        ),
        "session_mode": args.session_mode,
        "reasoning_tier": args.reasoning_tier,
        "cwd": str(args.cwd),
        "packet": str(args.packet),
        "permission_mode": args.permission_mode,
        "reuse_mode": args.reuse_mode,
        "next_expected_use": args.next_expected_use,
        "close_or_keep": args.close_or_keep,
        "terminal_window_ids": sorted({ref["window_id"] for ref in refs if ref.get("window_id")}),
        "terminal_ttys": sorted({ref["tty"] for ref in refs if ref.get("tty")}),
        "terminal_windows": describe_lane_refs(refs),
        "status": "open",
        "last_action": action,
        "updated_at": now_iso(),
    }
    save_registry(args.registry, registry)


def adopt_lane(args: argparse.Namespace) -> int:
    validate_lifecycle(args)
    matching_windows = visible_lane_windows(args.lane_id)
    if not matching_windows:
        raise SystemExit(f"cannot adopt lane; no visible Terminal window for --name {args.lane_id}")
    record_launch(args, action="adopted")
    payload = {
        "adopted": args.lane_id,
        "matching_windows": matching_windows,
        "registry": str(args.registry),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    args = parse_args()
    if args.list or args.status:
        return print_status(args)
    if not args.lane_id:
        raise SystemExit("--lane-id is required")
    if args.close:
        return close_lane(args.lane_id, args.registry, dry_run=args.dry_run)
    if args.adopt:
        return adopt_lane(args)
    if not args.cwd.is_dir():
        raise SystemExit(f"--cwd does not exist or is not a directory: {args.cwd}")
    if args.packet is None:
        raise SystemExit("--packet is required unless --close is used")
    if not args.packet.is_file():
        raise SystemExit(f"--packet does not exist: {args.packet}")
    validate_lifecycle(args)

    registry = load_registry(args.registry)
    validate_lane_id_route(registry, args)
    same_route = matching_open_registry_entries(
        registry,
        cwd=args.cwd,
        loop_id=args.loop_id,
        lane_role=args.lane_role,
        lane_scope=args.lane_scope,
    )
    if args.dry_run:
        same_lane_windows = []
        window_warning = None
    else:
        same_lane_windows, window_warning = visible_lane_windows_with_warning(args.lane_id)
        if window_warning:
            print(f"warning: Terminal window scan failed; registry gate still applies: {window_warning}")
    if args.session_mode == "reuse":
        reusable_ids = [entry.get("lane_id", "") for entry in same_route if entry.get("lane_id") != args.lane_id]
        if reusable_ids and not args.reuse:
            raise SystemExit(
                "existing reusable Claude lane for this cwd/loop/role/scope: "
                + ", ".join(reusable_ids)
                + "; use that --lane-id with --reuse or close it first"
            )
        if same_lane_windows and not args.reuse:
            raise SystemExit("lane already has a visible Terminal window; use --reuse or choose a fresh lane id")
    elif same_lane_windows:
        raise SystemExit("fresh/one_shot lane id already has a visible Terminal window; close it or choose a new lane id")
    elif same_route:
        open_ids = ", ".join(entry.get("lane_id", "") for entry in same_route)
        raise SystemExit(
            "existing open Claude lane for this exact route: "
            + open_ids
            + "; close it, reuse it if allowed, or choose a different --lane-scope"
        )

    instruction = "Read and execute this packet exactly: " + str(args.packet)
    claude_cmd = (
        f"cd {shlex.quote(str(args.cwd))}; "
        f"claude --name {shlex.quote(args.lane_id)} "
        f"--permission-mode {shlex.quote(args.permission_mode)} "
        f"{shlex.quote(instruction)}"
    )
    if args.dry_run:
        print(instruction if args.reuse and args.reuse_mode == "interactive" else claude_cmd)
        return 0
    if args.reuse:
        text = instruction if args.reuse_mode == "interactive" else claude_cmd
        result = send_to_existing_lane(args.lane_id, text, dry_run=False)
        record_launch(args, action="reused")
        return result

    script = f"tell {TERMINAL_APP} to do script {applescript_string(claude_cmd)}"
    subprocess.run(["osascript", "-e", script, "-e", f"tell {TERMINAL_APP} to activate"], check=True)
    record_launch(args, action="launched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

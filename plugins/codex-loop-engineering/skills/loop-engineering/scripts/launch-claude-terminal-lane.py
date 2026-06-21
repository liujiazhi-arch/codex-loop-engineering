#!/usr/bin/env python3
"""Launch a visible named Claude Terminal lane.

The lane must write its own output artifact and done JSON as instructed by the
packet. Codex should validate those files instead of scraping terminal chat.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch a named Claude Terminal lane.")
    parser.add_argument("--lane-id", required=True, help="Claude lane/session name.")
    parser.add_argument("--packet", type=Path, help="Packet path Claude should execute. Required unless --close is used.")
    parser.add_argument("--cwd", type=Path, default=Path.cwd(), help="Project working directory.")
    parser.add_argument(
        "--permission-mode",
        default="acceptEdits",
        choices=["acceptEdits", "dontAsk", "default", "plan", "auto", "bypassPermissions"],
        help="Use acceptEdits when Claude must write output/done artifacts.",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="If a Terminal window/tab with this lane id exists, send the packet there instead of opening a new lane.",
    )
    parser.add_argument(
        "--close",
        action="store_true",
        help="Close Terminal windows whose title contains this lane id, then exit.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print command without launching Terminal.")
    return parser.parse_args()


def osascript(script: str) -> None:
    subprocess.run(["osascript", "-e", script], check=True)


def applescript_string(value: str) -> str:
    return repr(value)


def close_lane(lane_id: str, *, dry_run: bool) -> int:
    script = f"""
tell application "Terminal"
  repeat with w in windows
    if name of w contains {applescript_string(lane_id)} then
      close w
      return
    end if
  end repeat
end tell
"""
    if dry_run:
        print(script.strip())
        return 0
    osascript(script)
    return 0


def send_to_existing_lane(lane_id: str, command: str, *, dry_run: bool) -> int:
    script = f"""
tell application "Terminal"
  repeat with w in windows
    if name of w contains {applescript_string(lane_id)} then
      do script {applescript_string(command)} in selected tab of w
      set frontmost of w to true
      activate
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


def main() -> int:
    args = parse_args()
    if args.close:
        return close_lane(args.lane_id, dry_run=args.dry_run)
    if not args.cwd.is_dir():
        raise SystemExit(f"--cwd does not exist or is not a directory: {args.cwd}")
    if args.packet is None:
        raise SystemExit("--packet is required unless --close is used")
    if not args.packet.is_file():
        raise SystemExit(f"--packet does not exist: {args.packet}")

    claude_cmd = (
        f"cd {shlex.quote(str(args.cwd))}; "
        f"claude --name {shlex.quote(args.lane_id)} "
        f"--permission-mode {shlex.quote(args.permission_mode)} "
        f"{shlex.quote('Read and execute this packet exactly: ' + str(args.packet))}"
    )
    if args.dry_run:
        print(claude_cmd)
        return 0
    if args.reuse:
        return send_to_existing_lane(args.lane_id, claude_cmd, dry_run=False)

    script = f'tell application "Terminal" to do script {claude_cmd!r}'
    subprocess.run(["osascript", "-e", script, "-e", 'tell application "Terminal" to activate'], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

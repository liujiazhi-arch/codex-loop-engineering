#!/usr/bin/env python3
"""Regression tests for Claude Terminal lane lifecycle and close behavior."""

from __future__ import annotations

import importlib.util
import json
import os
import pty
import subprocess
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).with_name("launch-claude-terminal-lane.py")
spec = importlib.util.spec_from_file_location("launch_claude_terminal_lane", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import launcher: {SCRIPT}")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def args(**overrides: object) -> SimpleNamespace:
    defaults = {
        "loop_id": "TEST-LOOP",
        "lane_role": "review",
        "lane_scope": "test-scope",
        "session_mode": "fresh",
        "reasoning_tier": "high",
        "next_expected_use": "none",
        "close_or_keep": "close",
        "reuse": False,
        "lane_id": "test-lane",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def assert_raises_system_exit(expected: str, fn: object, *fn_args: object) -> None:
    try:
        fn(*fn_args)
    except SystemExit as exc:
        message = str(exc)
        assert expected in message, f"expected {expected!r} in {message!r}"
        return
    raise AssertionError(f"expected SystemExit containing {expected!r}")


def test_companion_lifecycle_rejects_disposable_close() -> None:
    assert_raises_system_exit(
        "companion lanes must use --session-mode reuse",
        launcher.validate_lifecycle,
        args(
            lane_role="product-design-companion",
            session_mode="fresh",
            close_or_keep="close",
            next_expected_use="none",
        ),
    )
    assert_raises_system_exit(
        "companion lanes require a concrete future use",
        launcher.validate_lifecycle,
        args(
            lane_role="planning-companion",
            session_mode="reuse",
            close_or_keep="close",
            next_expected_use="none",
        ),
    )
    assert_raises_system_exit(
        "companion lanes must use --session-mode reuse",
        launcher.validate_lifecycle,
        args(
            lane_role="ux-companion",
            session_mode="fresh",
            close_or_keep="close",
            next_expected_use="none",
        ),
    )


def test_companion_lifecycle_accepts_reuse_checkpoint() -> None:
    launcher.validate_lifecycle(
        args(
            lane_role="strategy-companion",
            session_mode="reuse",
            close_or_keep="checkpoint",
            next_expected_use="continue strategy after next user checkpoint",
        )
    )


def test_one_shot_lifecycle_can_close() -> None:
    launcher.validate_lifecycle(
        args(
            lane_role="one-shot",
            session_mode="one_shot",
            close_or_keep="close",
            next_expected_use="none",
        )
    )


def test_planning_named_lane_cannot_be_one_shot() -> None:
    assert_raises_system_exit(
        "claude-planning-* lanes are planning/product companions",
        launcher.validate_lifecycle,
        args(
            lane_id="claude-planning-product-workstream-20260622",
            lane_role="one-shot",
            lane_scope="product-workstream-apply-contract",
            session_mode="one_shot",
            close_or_keep="close",
            next_expected_use="none",
        ),
    )


def test_tty_normalization() -> None:
    assert launcher.normalize_tty("/dev/ttys003") == "ttys003"
    assert launcher.normalize_tty("ttys004") == "ttys004"


def test_interrupt_ttys_kills_matching_lane_process() -> None:
    lane_id = f"test-close-lane-{os.getpid()}"
    child_pid, master_fd = pty.fork()
    if child_pid == 0:
        os.execl("/bin/zsh", "zsh", "-lc", f"exec -a 'claude --name {lane_id} test' sleep 600")
    try:
        tty_name = ""
        deadline = time.time() + 4
        while time.time() < deadline:
            output = subprocess.run(
                ["ps", "-p", str(child_pid), "-o", "tty="],
                text=True,
                capture_output=True,
                check=False,
            ).stdout.strip()
            if output and output != "?":
                tty_name = output
                break
            time.sleep(0.1)
        assert tty_name, "test process did not get a controlling PTY"

        deadline = time.time() + 4
        while time.time() < deadline:
            if launcher.live_lane_processes(lane_id, ["/dev/" + tty_name]):
                break
            time.sleep(0.1)
        assert launcher.live_lane_processes(lane_id, ["/dev/" + tty_name]), "test process was not visible on the PTY"

        remaining = launcher.interrupt_ttys(["/dev/" + tty_name], lane_id=lane_id)
        assert remaining == []
        waited_pid, status = os.waitpid(child_pid, 0)
        assert waited_pid == child_pid
        assert os.WIFSIGNALED(status) or os.WIFEXITED(status)
    finally:
        try:
            os.kill(child_pid, 9)
        except ProcessLookupError:
            pass
        try:
            os.waitpid(child_pid, os.WNOHANG)
        except ChildProcessError:
            pass
        os.close(master_fd)


def test_close_lane_records_close_failed_when_process_survives() -> None:
    originals = {
        "matching_lane_ttys": launcher.matching_lane_ttys,
        "interrupt_ttys": launcher.interrupt_ttys,
    }
    lane_id = "test-close-failed-process"
    try:
        launcher.matching_lane_ttys = lambda lane, entry=None: ["/dev/ttys999"]
        launcher.interrupt_ttys = lambda ttys, lane_id: [
            {"pid": "123", "tty": "ttys999", "stat": "S", "command": f"claude --name {lane_id}"}
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = Path(tmpdir) / "registry.json"
            result = launcher.close_lane(lane_id, registry, dry_run=False)
            payload = json.loads(registry.read_text(encoding="utf-8"))
        assert result == 2
        assert payload[lane_id]["status"] == "close_failed"
        assert payload[lane_id]["live_processes_after_interrupt"]
    finally:
        launcher.matching_lane_ttys = originals["matching_lane_ttys"]
        launcher.interrupt_ttys = originals["interrupt_ttys"]


def test_close_lane_records_close_failed_when_window_survives() -> None:
    originals = {
        "matching_lane_ttys": launcher.matching_lane_ttys,
        "interrupt_ttys": launcher.interrupt_ttys,
        "osascript": launcher.osascript,
        "visible_lane_windows": launcher.visible_lane_windows,
    }
    lane_id = "test-close-failed-window"
    try:
        launcher.matching_lane_ttys = lambda lane, entry=None: []
        launcher.interrupt_ttys = lambda ttys, lane_id: []
        launcher.osascript = lambda script: "1"
        launcher.visible_lane_windows = lambda lane, entry=None: [f"claude --name {lane} still visible"]
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = Path(tmpdir) / "registry.json"
            result = launcher.close_lane(lane_id, registry, dry_run=False)
            payload = json.loads(registry.read_text(encoding="utf-8"))
        assert result == 2
        assert payload[lane_id]["status"] == "close_failed"
        assert payload[lane_id]["remaining_windows"]
    finally:
        launcher.matching_lane_ttys = originals["matching_lane_ttys"]
        launcher.interrupt_ttys = originals["interrupt_ttys"]
        launcher.osascript = originals["osascript"]
        launcher.visible_lane_windows = originals["visible_lane_windows"]


def test_close_lane_uses_registry_refs_when_title_lost() -> None:
    originals = {
        "matching_lane_ttys": launcher.matching_lane_ttys,
        "interrupt_ttys": launcher.interrupt_ttys,
        "osascript": launcher.osascript,
        "visible_lane_windows": launcher.visible_lane_windows,
    }
    lane_id = "test-title-lost"
    observed: dict[str, object] = {}
    try:
        def fake_matching_ttys(lane: str, entry: dict[str, object] | None = None) -> list[str]:
            observed["matching_entry"] = entry
            return list(entry.get("terminal_ttys", [])) if entry else []

        def fake_osascript(script: str) -> str:
            observed["close_script"] = script
            assert "42460" in script
            assert "/dev/ttys000" in script
            return "1"

        launcher.matching_lane_ttys = fake_matching_ttys
        launcher.interrupt_ttys = lambda ttys, lane_id: []
        launcher.osascript = fake_osascript
        launcher.visible_lane_windows = lambda lane, entry=None: []
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = Path(tmpdir) / "registry.json"
            registry.write_text(
                json.dumps(
                    {
                        lane_id: {
                            "lane_id": lane_id,
                            "terminal_window_ids": ["42460"],
                            "terminal_ttys": ["/dev/ttys000"],
                        }
                    }
                ),
                encoding="utf-8",
            )
            result = launcher.close_lane(lane_id, registry, dry_run=False)
            payload = json.loads(registry.read_text(encoding="utf-8"))
        assert result == 0
        assert payload[lane_id]["status"] == "closed"
        assert payload[lane_id]["closed_windows"] == "1"
        assert payload[lane_id]["interrupted_ttys"] == ["/dev/ttys000"]
        assert observed["matching_entry"]["terminal_window_ids"] == ["42460"]
    finally:
        launcher.matching_lane_ttys = originals["matching_lane_ttys"]
        launcher.interrupt_ttys = originals["interrupt_ttys"]
        launcher.osascript = originals["osascript"]
        launcher.visible_lane_windows = originals["visible_lane_windows"]


def main() -> int:
    tests = [
        test_companion_lifecycle_rejects_disposable_close,
        test_companion_lifecycle_accepts_reuse_checkpoint,
        test_one_shot_lifecycle_can_close,
        test_planning_named_lane_cannot_be_one_shot,
        test_tty_normalization,
        test_interrupt_ttys_kills_matching_lane_process,
        test_close_lane_records_close_failed_when_process_survives,
        test_close_lane_records_close_failed_when_window_survives,
        test_close_lane_uses_registry_refs_when_title_lost,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_ACTIVE_WINDOW_SECONDS = 30 * 60


class ConfigError(ValueError):
    """Raised when repo-managed caffeinate config is invalid."""


@dataclass(frozen=True)
class RuntimeConfig:
    action: str
    repo_root: Path
    repo_slug: str
    pid_file: Path
    log_file: Path
    meta_file: Path
    activity_file: Path
    legacy_pid_file: Path
    legacy_log_file: Path
    legacy_meta_file: Path
    legacy_activity_file: Path
    caffeinate_cmd: str
    match_pattern: str
    launcher_python: str
    detached_launcher: Path
    active_window_seconds: int
    allow_global_cleanup: bool
    uname_bin: str
    pgrep_bin: str
    pmset_bin: str
    ps_bin: str


@dataclass(frozen=True)
class ProcessState:
    status: str
    pid: int | None = None
    command: str = ""
    reason: str = ""


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _utc_now_text() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


def _read_bool_env(name: str) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return False
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigError(
        f"{name} must be a boolean flag: 1/0, true/false, yes/no, or on/off."
    )


def _read_positive_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        parsed = int(raw)
    except ValueError:
        raise ConfigError(f"{name} must be a positive integer.") from None
    if parsed <= 0:
        raise ConfigError(f"{name} must be a positive integer.")
    return parsed


def _read_non_empty_env(name: str, default: str) -> str:
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = raw.strip()
    if not value:
        raise ConfigError(f"{name} must not be empty when set.")
    return value


def _default_meta_file(pid_file: Path) -> Path:
    if pid_file.suffix == ".pid":
        return pid_file.with_suffix(".meta.json")
    return pid_file.with_name(f"{pid_file.name}.meta.json")


def _default_activity_file(pid_file: Path) -> Path:
    if pid_file.suffix == ".pid":
        return pid_file.with_suffix(".activity.json")
    return pid_file.with_name(f"{pid_file.name}.activity.json")


def _default_runtime_root() -> Path:
    return Path("/tmp") / "polinko-runtime"


def _legacy_runtime_file(repo_slug: str, suffix: str) -> Path:
    return Path("/tmp") / f"{repo_slug}-caffeinate{suffix}"


def _path_from_env(name: str, default: Path) -> Path:
    raw = os.environ.get(name, "").strip()
    return Path(raw).expanduser() if raw else default


def _git_value(repo_root: Path, *args: str, fallback: str = "unknown") -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    value = result.stdout.strip()
    return value or fallback


def _branch(repo_root: Path) -> str:
    return _git_value(repo_root, "branch", "--show-current")


def _commit(repo_root: Path) -> str:
    return _git_value(repo_root, "rev-parse", "--short", "HEAD")


def _load_config(action: str) -> RuntimeConfig:
    repo_root = Path(os.environ.get("POLINKO_REPO_ROOT", Path.cwd())).resolve()
    repo_slug = _read_non_empty_env("CAFFEINATE_REPO_SLUG", repo_root.name)

    runtime_root = _path_from_env("CAFFEINATE_RUNTIME_ROOT", _default_runtime_root())
    state_dir = _path_from_env("CAFFEINATE_STATE_DIR", runtime_root / repo_slug)
    pid_file = _path_from_env("CAFFEINATE_PID_FILE", state_dir / "caffeinate.pid")
    log_file = _path_from_env("CAFFEINATE_LOG", state_dir / "caffeinate.log")
    meta_file = _path_from_env("CAFFEINATE_META_FILE", _default_meta_file(pid_file))
    activity_file = _path_from_env(
        "CAFFEINATE_ACTIVITY_FILE", _default_activity_file(pid_file)
    )

    return RuntimeConfig(
        action=action,
        repo_root=repo_root,
        repo_slug=repo_slug,
        pid_file=pid_file,
        log_file=log_file,
        meta_file=meta_file,
        activity_file=activity_file,
        legacy_pid_file=_path_from_env(
            "CAFFEINATE_LEGACY_PID_FILE",
            _legacy_runtime_file(repo_slug, ".pid"),
        ),
        legacy_log_file=_path_from_env(
            "CAFFEINATE_LEGACY_LOG",
            _legacy_runtime_file(repo_slug, ".log"),
        ),
        legacy_meta_file=_path_from_env(
            "CAFFEINATE_LEGACY_META_FILE",
            _legacy_runtime_file(repo_slug, ".meta.json"),
        ),
        legacy_activity_file=_path_from_env(
            "CAFFEINATE_LEGACY_ACTIVITY_FILE",
            _legacy_runtime_file(repo_slug, ".activity.json"),
        ),
        caffeinate_cmd=os.environ.get("CAFFEINATE_CMD", "/usr/bin/caffeinate -d -i -m"),
        match_pattern=os.environ.get(
            "CAFFEINATE_MATCH_PATTERN", r"^/usr/bin/caffeinate -d -i -m( |$)"
        ),
        launcher_python=os.environ.get("CAFFEINATE_LAUNCHER_PYTHON", sys.executable),
        detached_launcher=_path_from_env(
            "CAFFEINATE_DETACHED_LAUNCHER",
            repo_root / "tools" / "launch_detached_process.py",
        ),
        active_window_seconds=_read_positive_int_env(
            "CAFFEINATE_ACTIVE_WINDOW_SECONDS", DEFAULT_ACTIVE_WINDOW_SECONDS
        ),
        allow_global_cleanup=_read_bool_env("CAFFEINATE_ALLOW_GLOBAL_CLEANUP"),
        uname_bin=os.environ.get("UNAME_BIN", "uname"),
        pgrep_bin=os.environ.get("PGREP_BIN", "pgrep"),
        pmset_bin=os.environ.get("PMSET_BIN", "/usr/bin/pmset"),
        ps_bin=os.environ.get("PS_BIN", "ps"),
    )


def _validate_config(config: RuntimeConfig) -> None:
    if not config.caffeinate_cmd.strip():
        raise ConfigError("CAFFEINATE_CMD must not be empty.")
    if not config.match_pattern.strip():
        raise ConfigError("CAFFEINATE_MATCH_PATTERN must not be empty.")
    try:
        re.compile(config.match_pattern)
    except re.error as exc:
        raise ConfigError(f"CAFFEINATE_MATCH_PATTERN must be a valid regex: {exc}.")


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    tmp.replace(path)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _read_pid(path: Path) -> int | None:
    try:
        raw = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not raw.isdigit():
        return None
    pid = int(raw)
    return pid if pid > 0 else None


def _remove_path(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return


def _prepare_output_path(path: Path, label: str) -> bool:
    if path.exists() and path.is_dir():
        print(
            f"caffeinate runtime error: {label} path is a directory: {path}",
            file=sys.stderr,
        )
        return False
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(
            f"caffeinate runtime error: failed to prepare {label} parent "
            f"{path.parent}: {exc}",
            file=sys.stderr,
        )
        return False
    return True


def _prepare_runtime_paths(config: RuntimeConfig) -> bool:
    return all(
        _prepare_output_path(path, label)
        for path, label in (
            (config.pid_file, "PID file"),
            (config.log_file, "log file"),
            (config.meta_file, "metadata file"),
            (config.activity_file, "activity metadata"),
        )
    )


def _pid_live(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _process_command(config: RuntimeConfig, pid: int) -> str:
    try:
        result = subprocess.run(
            [config.ps_bin, "-p", str(pid), "-o", "command="],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    return result.stdout.strip()


def _process_stat(config: RuntimeConfig, pid: int) -> str:
    try:
        result = subprocess.run(
            [config.ps_bin, "-p", str(pid), "-o", "stat="],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    return result.stdout.strip()


def _pid_stopped(config: RuntimeConfig, pid: int) -> bool:
    if not _pid_live(pid):
        return True
    return _process_stat(config, pid).startswith("Z")


def _command_matches(config: RuntimeConfig, command: str) -> bool:
    if not command:
        return False
    try:
        return re.search(config.match_pattern, command) is not None
    except re.error:
        return False


def _evaluate_pid_file(config: RuntimeConfig) -> ProcessState:
    pid = _read_pid(config.pid_file)
    if pid is None:
        return ProcessState("missing", reason="PID file missing or invalid")
    if _pid_stopped(config, pid):
        return ProcessState("stale", pid=pid, reason="PID is not live")

    command = _process_command(config, pid)
    if not _command_matches(config, command):
        return ProcessState(
            "live-non-owned",
            pid=pid,
            command=command,
            reason="process command does not match configured pattern",
        )

    meta = _load_json(config.meta_file)
    if meta is None:
        return ProcessState("legacy-owned", pid=pid, command=command)

    expected_root = str(config.repo_root)
    if meta.get("repo_root") != expected_root:
        return ProcessState(
            "live-non-owned",
            pid=pid,
            command=command,
            reason="metadata repo_root does not match current repo",
        )
    if meta.get("pid") != pid:
        return ProcessState(
            "live-non-owned",
            pid=pid,
            command=command,
            reason="metadata PID does not match PID file",
        )
    if meta.get("runner") != "caffeinate":
        return ProcessState(
            "live-non-owned",
            pid=pid,
            command=command,
            reason="metadata runner does not match caffeinate",
        )

    return ProcessState("owned", pid=pid, command=command)


def _metadata_payload(config: RuntimeConfig, pid: int) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "runner": "caffeinate",
        "repo_slug": config.repo_slug,
        "repo_root": str(config.repo_root),
        "branch": _branch(config.repo_root),
        "commit": _commit(config.repo_root),
        "pid": pid,
        "command": config.caffeinate_cmd,
        "match_pattern": config.match_pattern,
        "started_at": _utc_now_text(),
        "pid_file": str(config.pid_file),
        "log_file": str(config.log_file),
    }


def _write_caffeinate_metadata(config: RuntimeConfig, pid: int) -> None:
    _write_json_atomic(config.meta_file, _metadata_payload(config, pid))


def _write_activity(config: RuntimeConfig, label: str, target: str) -> None:
    _write_json_atomic(
        config.activity_file,
        {
            "schema_version": SCHEMA_VERSION,
            "repo_slug": config.repo_slug,
            "repo_root": str(config.repo_root),
            "branch": _branch(config.repo_root),
            "commit": _commit(config.repo_root),
            "last_activity_at": _utc_now_text(),
            "last_activity_label": label,
            "last_activity_target": target,
        },
    )


def activity(config: RuntimeConfig) -> int:
    if not _prepare_output_path(config.activity_file, "activity metadata"):
        return 1
    target = _read_non_empty_env("CAFFEINATE_ACTIVITY_TARGET", config.action)
    label = _read_non_empty_env("CAFFEINATE_ACTIVITY_LABEL", f"make {target}")
    _write_activity(config, label, target)
    return 0


def _remove_runtime_metadata(config: RuntimeConfig) -> None:
    _remove_path(config.pid_file)
    _remove_path(config.meta_file)


def _legacy_config(config: RuntimeConfig) -> RuntimeConfig:
    return replace(
        config,
        pid_file=config.legacy_pid_file,
        log_file=config.legacy_log_file,
        meta_file=config.legacy_meta_file,
        activity_file=config.legacy_activity_file,
    )


def _move_legacy_file(source: Path, destination: Path) -> None:
    if not source.exists() or destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.replace(destination)


def _migrate_legacy_runtime_state(config: RuntimeConfig) -> None:
    if config.pid_file.exists() or config.legacy_pid_file == config.pid_file:
        return

    legacy = _legacy_config(config)
    state = _evaluate_pid_file(legacy)
    if state.status == "missing":
        return
    if state.status == "live-non-owned":
        print("Flat caffeinate PID reference is non-owned; leaving it untouched.")
        return
    if state.status == "stale":
        _remove_runtime_metadata(legacy)
        print("Cleaned orphaned flat caffeinate PID metadata.")
        return

    _move_legacy_file(config.legacy_pid_file, config.pid_file)
    _move_legacy_file(config.legacy_log_file, config.log_file)
    _move_legacy_file(config.legacy_meta_file, config.meta_file)
    _move_legacy_file(config.legacy_activity_file, config.activity_file)
    if state.pid is not None:
        _write_caffeinate_metadata(config, state.pid)
    print("Migrated flat caffeinate runtime files into repo namespace.")


def _is_darwin(config: RuntimeConfig) -> bool:
    try:
        result = subprocess.run(
            [config.uname_bin, "-s"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    return result.stdout.strip() == "Darwin"


def _skip_unless_darwin(config: RuntimeConfig) -> bool:
    if _is_darwin(config):
        return False
    if config.action == "status":
        print("caffeinate status is only available on macOS.")
    else:
        print("caffeinate is macOS-only; skipping.")
    return True


def _require_process_inspection(config: RuntimeConfig) -> bool:
    if shutil.which(config.ps_bin) is not None:
        return True
    print(
        f"caffeinate config error: PS_BIN command not found: {config.ps_bin}",
        file=sys.stderr,
    )
    return False


def _launch_detached(config: RuntimeConfig) -> bool:
    try:
        result = subprocess.run(
            [
                config.launcher_python,
                str(config.detached_launcher),
                "--pid-file",
                str(config.pid_file),
                "--log-file",
                str(config.log_file),
                "--command-string",
                config.caffeinate_cmd,
            ],
            cwd=config.repo_root,
            check=False,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0


def _find_matching_pids(config: RuntimeConfig) -> list[int]:
    try:
        result = subprocess.run(
            [config.pgrep_bin, "-f", config.match_pattern],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return []
    pids: list[int] = []
    for line in result.stdout.splitlines():
        value = line.strip()
        if value.isdigit():
            pids.append(int(value))
    return pids


def _terminate_pid(config: RuntimeConfig, pid: int) -> bool:
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    if _wait_for_pid_stop(config, pid):
        return True
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return _wait_for_pid_stop(config, pid)


def _wait_for_pid_stop(
    config: RuntimeConfig, pid: int, *, attempts: int = 30, delay_seconds: float = 0.1
) -> bool:
    for _ in range(attempts):
        if _pid_stopped(config, pid):
            return True
        time.sleep(delay_seconds)
    return _pid_stopped(config, pid)


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _format_duration(seconds: float) -> str:
    total = max(0, int(seconds))
    days, remainder = divmod(total, 24 * 60 * 60)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, secs = divmod(remainder, 60)
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m"
    return f"{secs}s"


def _activity_state(config: RuntimeConfig) -> tuple[str, str]:
    activity = _load_json(config.activity_file)
    if activity is None:
        return "QUIET", "no recorded repo activity"
    if activity.get("repo_root") != str(config.repo_root):
        return "QUIET", "activity metadata belongs to another repo"

    timestamp = _parse_timestamp(activity.get("last_activity_at"))
    label = str(activity.get("last_activity_label") or "unknown activity")
    if timestamp is None:
        return "QUIET", f"invalid activity timestamp via {label}"

    age = (_utc_now() - timestamp).total_seconds()
    detail = f"{_format_duration(age)} ago via {label}"
    if age <= config.active_window_seconds:
        return "ACTIVE", detail
    return "QUIET", detail


def _metadata_started_age(config: RuntimeConfig) -> str:
    metadata = _load_json(config.meta_file)
    if metadata is None:
        return "unknown"
    timestamp = _parse_timestamp(metadata.get("started_at"))
    if timestamp is None:
        return "unknown"
    return _format_duration((_utc_now() - timestamp).total_seconds())


def _wake_assertion_text(config: RuntimeConfig) -> tuple[str, str]:
    try:
        result = subprocess.run(
            [config.pmset_bin, "-g", "assertions"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return "UNKNOWN", ""
    if result.returncode != 0:
        return "UNKNOWN", ""
    lines = [
        line
        for line in result.stdout.splitlines()
        if any(
            token in line
            for token in (
                "PreventUserIdleDisplaySleep",
                "PreventUserIdleSystemSleep",
                "PreventDiskIdle",
                "caffeinate",
            )
        )
    ]
    return ("PRESENT" if lines else "ABSENT"), "\n".join(lines)


def _branch_commit(config: RuntimeConfig) -> str:
    return f"{_branch(config.repo_root)} @ {_commit(config.repo_root)}"


def _print_repo_context(config: RuntimeConfig) -> None:
    print(f"Repo: {config.repo_slug}")
    print(f"Repo root: {config.repo_root}")


def _print_owned_status(config: RuntimeConfig, pid: int) -> None:
    state, detail = _activity_state(config)
    wake_state, wake_lines = _wake_assertion_text(config)
    print(f"Managed caffeinate: {state}")
    _print_repo_context(config)
    print(f"PID: {pid}")
    print(f"Wake-lock age: {_metadata_started_age(config)}")
    print(f"Last repo activity: {detail}")
    print(f"Branch: {_branch_commit(config)}")
    print(f"Wake assertion: {wake_state}")
    if wake_lines:
        print(wake_lines)


def start(config: RuntimeConfig) -> int:
    if _skip_unless_darwin(config):
        return 0
    if not _require_process_inspection(config):
        return 2
    if not _prepare_runtime_paths(config):
        return 1

    _migrate_legacy_runtime_state(config)

    state = _evaluate_pid_file(config)
    if state.status == "owned" and state.pid is not None:
        _write_activity(config, "make caffeinate", "caffeinate")
        print(f"caffeinate already running (PID {state.pid}).")
        return 0
    if state.status == "legacy-owned" and state.pid is not None:
        _write_caffeinate_metadata(config, state.pid)
        _write_activity(config, "make caffeinate", "caffeinate")
        print(f"caffeinate already running (PID {state.pid}); metadata refreshed.")
        return 0
    if state.status in {"stale", "live-non-owned"}:
        if state.status == "live-non-owned" and state.pid is not None:
            print(
                f"Cleaned non-owned caffeinate PID reference (PID {state.pid}); "
                "live process preserved."
            )
        else:
            print("Stale PID file found; cleaning up.")
        _remove_runtime_metadata(config)

    unmanaged = [
        pid
        for pid in _find_matching_pids(config)
        if pid != os.getpid() and pid != _read_pid(config.pid_file)
    ]
    if unmanaged:
        rendered = " ".join(str(pid) for pid in unmanaged)
        print(f"Unmanaged matching caffeinate detected (PID {rendered}); not adopted.")

    if not _launch_detached(config):
        _remove_runtime_metadata(config)
        print("Failed to start caffeinate.")
        return 1

    pid = _read_pid(config.pid_file)
    time.sleep(0.1)
    if pid is None or not _pid_live(pid):
        _remove_runtime_metadata(config)
        print("Failed to start caffeinate.")
        return 1

    command = _process_command(config, pid)
    if not _command_matches(config, command):
        _terminate_pid(config, pid)
        _remove_runtime_metadata(config)
        print("Failed to start caffeinate: launched process did not match pattern.")
        return 1

    _write_caffeinate_metadata(config, pid)
    _write_activity(config, "make caffeinate", "caffeinate")
    print(f"caffeinate started (PID {pid}).")
    return 0


def stop(config: RuntimeConfig, *, quiet_missing: bool = False) -> int:
    if _skip_unless_darwin(config):
        return 0
    if not _require_process_inspection(config):
        return 2
    if not _prepare_runtime_paths(config):
        return 1

    _migrate_legacy_runtime_state(config)
    state = _evaluate_pid_file(config)
    if state.status == "missing":
        _remove_runtime_metadata(config)
        if not quiet_missing:
            print("No managed caffeinate PID file found.")
        return 0
    if state.status in {"owned", "legacy-owned"} and state.pid is not None:
        if not _terminate_pid(config, state.pid):
            print(f"Failed to stop caffeinate (PID {state.pid}).")
            return 1
        _remove_runtime_metadata(config)
        _write_activity(config, "make decaffeinate", "decaffeinate")
        print(f"caffeinate stopped (PID {state.pid}).")
        return 0

    if state.status == "live-non-owned" and state.pid is not None:
        _remove_runtime_metadata(config)
        _write_activity(config, "make decaffeinate", "decaffeinate")
        print(
            f"Cleaned non-owned caffeinate PID reference (PID {state.pid}); "
            "live process preserved."
        )
        return 0

    _remove_runtime_metadata(config)
    _write_activity(config, "make decaffeinate", "decaffeinate")
    print("Stale PID file found; cleaning up.")
    return 0


def stop_all(config: RuntimeConfig) -> int:
    if _skip_unless_darwin(config):
        return 0

    scoped_result = stop(config, quiet_missing=True)
    if scoped_result != 0:
        return scoped_result

    _remove_runtime_metadata(config)
    _write_activity(config, "make caffeinate-off-all", "caffeinate-off-all")

    if not config.allow_global_cleanup:
        print("Current repo caffeinate cleanup complete.")
        print(
            "Global caffeinate cleanup skipped; set "
            "CAFFEINATE_ALLOW_GLOBAL_CLEANUP=1 to stop matching leftovers."
        )
        return 0

    pids = [pid for pid in _find_matching_pids(config) if pid != os.getpid()]
    if not pids:
        print("No matching caffeinate processes running.")
        return 0

    stopped: list[int] = []
    failed: list[int] = []
    for pid in pids:
        if _terminate_pid(config, pid):
            stopped.append(pid)
        else:
            failed.append(pid)

    if stopped:
        rendered = " ".join(str(pid) for pid in stopped)
        print(f"Stopped matching caffeinate processes: {rendered}")
    if failed:
        rendered = " ".join(str(pid) for pid in failed)
        print(f"Failed to stop matching caffeinate processes: {rendered}")
        return 1
    return 0


def status(config: RuntimeConfig) -> int:
    if _skip_unless_darwin(config):
        return 0
    if not _require_process_inspection(config):
        return 2

    state = _evaluate_pid_file(config)
    if state.status == "owned" and state.pid is not None:
        _print_owned_status(config, state.pid)
    elif state.status == "legacy-owned" and state.pid is not None:
        print("Managed caffeinate: STALE")
        _print_repo_context(config)
        print(f"PID: {state.pid}")
        print("Reason: PID is live but metadata is missing")
        print("Action: run make caffeinate to refresh repo metadata")
    elif state.status == "missing":
        print("Managed caffeinate: OFF")
        _print_repo_context(config)
        print(f"Branch: {_branch_commit(config)}")
        _, detail = _activity_state(config)
        print(f"Last repo activity: {detail}")
        pids = [pid for pid in _find_matching_pids(config) if pid != os.getpid()]
        if pids:
            rendered = " ".join(str(pid) for pid in pids)
            print(
                f"Unmanaged caffeinate detected (PID {rendered}); not owned by this repo."
            )
        wake_state, wake_lines = _wake_assertion_text(config)
        print(f"Wake assertion: {wake_state}")
        if wake_lines:
            print(wake_lines)
    else:
        print("Managed caffeinate: STALE")
        _print_repo_context(config)
        if state.pid is not None:
            print(f"PID: {state.pid}")
        if state.reason:
            print(f"Reason: {state.reason}")
        print("Action: run make decaffeinate to clean repo PID metadata")
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manage repo-scoped caffeinate runtime state."
    )
    parser.add_argument(
        "action", choices=("start", "stop", "stop-all", "status", "activity")
    )
    args = parser.parse_args(argv)
    try:
        config = _load_config(args.action)
        _validate_config(config)
    except ConfigError as exc:
        print(f"caffeinate config error: {exc}", file=sys.stderr)
        return 2

    try:
        if args.action == "start":
            return start(config)
        if args.action == "stop":
            return stop(config)
        if args.action == "stop-all":
            return stop_all(config)
        if args.action == "status":
            return status(config)
        if args.action == "activity":
            return activity(config)
    except ConfigError as exc:
        print(f"caffeinate config error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Launch a detached child process, redirect logs, and write its PID."""

from __future__ import annotations

import argparse
import os
import signal
import shlex
import subprocess
import sys
from pathlib import Path


def _split_options_and_command(argv: list[str]) -> tuple[list[str], list[str]]:
    if "--" not in argv:
        return argv, []
    separator_index = argv.index("--")
    return argv[:separator_index], argv[separator_index + 1 :]


def _parse_args(argv: list[str]) -> tuple[Path, Path, list[str]]:
    option_args, command_args = _split_options_and_command(argv)
    parser = argparse.ArgumentParser(
        description=(
            "Launch a process in a detached child session, redirect output to a "
            "log file, and write the child PID to a PID file."
        )
    )
    parser.add_argument("--pid-file", required=True, type=Path)
    parser.add_argument("--log-file", required=True, type=Path)
    parser.add_argument(
        "--command-string",
        help="Shell-style command string to parse with shlex instead of -- args.",
    )
    args = parser.parse_args(option_args)

    if args.command_string and command_args:
        parser.error("use either --command-string or command args after --, not both")
    if args.command_string:
        try:
            command = shlex.split(args.command_string)
        except ValueError as exc:
            raise SystemExit(f"Invalid command string: {exc}") from exc
    else:
        command = command_args

    if not command:
        parser.error("missing command to launch")
    if not command[0].strip():
        parser.error("missing executable to launch")

    return args.pid_file, args.log_file, command


def _stop_unmanaged_child(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return

    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except OSError:
        process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        except OSError:
            process.kill()
        process.wait(timeout=2)


def main(argv: list[str] | None = None) -> int:
    pid_file, log_file, command = _parse_args(
        list(sys.argv[1:] if argv is None else argv)
    )

    pid_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("ab", buffering=0) as log:
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True,
            )
        except FileNotFoundError:
            print(
                f"launch-detached: command not found: {command[0]}",
                file=sys.stderr,
            )
            return 127
        except OSError as exc:
            print(
                f"launch-detached: failed to launch {command[0]}: {exc}",
                file=sys.stderr,
            )
            return 1

    try:
        pid_file.write_text(str(process.pid), encoding="utf-8")
    except OSError:
        _stop_unmanaged_child(process)
        raise

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

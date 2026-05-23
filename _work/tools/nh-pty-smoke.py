#!/usr/bin/env python3
"""Run a small NetHack tty smoke test through a pseudo terminal."""

import argparse
import fcntl
import os
import select
import signal
import struct
import subprocess
import sys
import termios
import time


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launch a tty NetHack command in a pty and check output."
    )
    parser.add_argument("--expect", action="append", default=[],
                        help="Text that must appear; may be repeated.")
    parser.add_argument("--forbid", action="append", default=[],
                        help="Text that must not appear; may be repeated.")
    parser.add_argument("--after-expect-send",
                        help="Text to send after initial expectations appear.")
    parser.add_argument("--post-expect", action="append", default=[],
                        help="Text required after --after-expect-send.")
    parser.add_argument("--timeout", type=float, default=10.0,
                        help="Seconds before the smoke test fails.")
    parser.add_argument("--cols", type=int, default=80,
                        help="Pseudo-terminal column count.")
    parser.add_argument("--rows", type=int, default=25,
                        help="Pseudo-terminal row count.")
    parser.add_argument("--quit", action="store_true",
                        help="Send #quit after expected text appears.")
    parser.add_argument("--log", help="Write raw captured terminal output.")
    parser.add_argument("command", nargs=argparse.REMAINDER,
                        help="Command to run, after --.")
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("missing command")
    if args.after_expect_send:
        args.after_expect_send = bytes(
            args.after_expect_send, "utf-8"
        ).decode("unicode_escape")
    return args


def set_winsize(fd, rows, cols):
    packed = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, packed)


def kill_process(proc):
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=2)


def write_log(path, raw):
    if path:
        with open(path, "wb") as handle:
            handle.write(raw)


def main():
    args = parse_args()
    master, slave = os.openpty()
    set_winsize(slave, args.rows, args.cols)

    env = os.environ.copy()
    env.setdefault("TERM", "xterm")
    env["COLUMNS"] = str(args.cols)
    env["LINES"] = str(args.rows)

    proc = subprocess.Popen(
        args.command,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        env=env,
        close_fds=True,
        start_new_session=True,
    )
    os.close(slave)

    deadline = time.monotonic() + args.timeout
    raw = bytearray()
    text = ""
    sent_quit = False
    confirmed_quit = False
    continued_notice = False
    last_more_at = -1
    last_end_at = -1
    sent_after_expect = False

    try:
        while True:
            if proc.poll() is not None:
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                missing = [expected for expected in args.expect
                           if expected not in text]
                write_log(args.log, raw)
                sys.stderr.write("timeout waiting for process")
                if missing:
                    sys.stderr.write("; missing: " + ", ".join(missing))
                sys.stderr.write("\n")
                return 124

            readable, _, _ = select.select([master], [], [], min(0.1, remaining))
            if readable:
                try:
                    chunk = os.read(master, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                raw.extend(chunk)
                text = raw.decode("utf-8", errors="ignore")

                for forbidden in args.forbid:
                    if forbidden in text:
                        write_log(args.log, raw)
                        sys.stderr.write(f"forbidden text appeared: {forbidden}\n")
                        return 1

                if not continued_notice and "Hit return to continue:" in text:
                    os.write(master, b"\r")
                    continued_notice = True

                more_at = text.rfind("--More--")
                if more_at > last_more_at:
                    os.write(master, b" ")
                    last_more_at = more_at

                expected_seen = all(expected in text for expected in args.expect)
                if (args.after_expect_send and expected_seen
                        and not sent_after_expect):
                    os.write(master, args.after_expect_send.encode("utf-8"))
                    sent_after_expect = True

                post_seen = all(expected in text for expected in args.post_expect)
                end_at = text.rfind("(end)")
                if post_seen and end_at > last_end_at:
                    os.write(master, b" ")
                    last_end_at = end_at
                    continue

                ready_to_quit = expected_seen and (
                    not args.post_expect or post_seen
                )
                if args.quit and ready_to_quit and not sent_quit:
                    os.write(master, b"#quit\r")
                    sent_quit = True
                if sent_quit and not confirmed_quit and "Really quit" in text:
                    os.write(master, b"yes\r")
                    confirmed_quit = True

        write_log(args.log, raw)

        missing = [expected for expected in args.expect + args.post_expect
                   if expected not in text]
        if missing:
            sys.stderr.write("missing expected text: " + ", ".join(missing) + "\n")
            return 1

        return proc.returncode or 0
    finally:
        kill_process(proc)
        os.close(master)


if __name__ == "__main__":
    raise SystemExit(main())

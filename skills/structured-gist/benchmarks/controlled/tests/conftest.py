"""Shared pytest setup for the controlled benchmark (tasks T002).

- Puts the controlled-benchmark root (CB), the semantic-compression scorer
  (SC/scoring), the frozen external-validation adapters and scripts
  (EV/adapters, EV/scripts) and the skill's linter directory
  (skills/structured-gist/tests) on sys.path, the same way
  EV/evaluation/score_semantic.py imports them.
- Provides a fake ``subprocess.run`` fixture that records argv, env and cwd,
  and a fake clock fixture.
- Installs an autouse guard that fails any test that tries to spawn a real
  model CLI (claude, agents-inc, codex, mask.sh, gask.sh, oask.sh) or to open
  a network socket. Tests never make a model or network call (research R15).

Bytecode writing is turned off so importing the frozen EV modules never
creates files inside the EV tree.
"""
from __future__ import annotations

import datetime as _dt
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

sys.dont_write_bytecode = True

CB = Path(__file__).resolve().parent.parent
SG = CB.parent.parent  # skills/structured-gist
SC = SG / "benchmarks" / "semantic-compression"
EV = SC / "external-validation"
REPO = SG.parent.parent

for _p in (SG / "tests", EV / "scripts", EV / "adapters", SC / "scoring", CB):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

# DomI contracts directory (DC). Optional: tests that compare against it skip
# when it is absent (for example on CI, which has no DomI checkout).
DC = Path(
    os.environ.get(
        "SG_BENCH_DC",
        str(
            Path.home()
            / "Projects/DomI/specs/consumers/structured-gist/specs/005-controlled-benchmark/contracts"
        ),
    )
)

BANNED_EXECUTABLES = frozenset(
    {"claude", "agents-inc", "codex", "mask.sh", "gask.sh", "oask.sh"}
)


class ForbiddenCall(AssertionError):
    """Raised when a test tries to reach a model CLI or the network."""


def _argv0_name(args) -> str:
    if isinstance(args, (str, bytes)):
        first = args.split()[0] if args.split() else ""
    else:
        seq = list(args)
        first = seq[0] if seq else ""
    if isinstance(first, bytes):
        first = first.decode("utf-8", "replace")
    return os.path.basename(str(first))


def _check_argv(args) -> None:
    name = _argv0_name(args)
    if name in BANNED_EXECUTABLES:
        raise ForbiddenCall(f"test tried to spawn a real model CLI: {name!r}")
    # `env X=Y claude ...` or `bash mask.sh ...` style indirection.
    if not isinstance(args, (str, bytes)):
        for tok in list(args)[1:3]:
            if os.path.basename(str(tok)) in BANNED_EXECUTABLES:
                raise ForbiddenCall(f"test tried to spawn a real model CLI via {name!r}: {tok!r}")


@pytest.fixture(autouse=True)
def _no_models_no_network(monkeypatch):
    real_popen = subprocess.Popen

    class GuardedPopen(real_popen):  # type: ignore[misc, valid-type]
        def __init__(self, args, *a, **kw):
            _check_argv(args)
            super().__init__(args, *a, **kw)

    monkeypatch.setattr(subprocess, "Popen", GuardedPopen)

    def _no_system(cmd):
        _check_argv(cmd)
        raise ForbiddenCall("os.system is not allowed in tests")

    monkeypatch.setattr(os, "system", _no_system)

    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex

    def _guard_connect(self, address, _real=real_connect):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            raise ForbiddenCall(f"test tried to open a network socket to {address!r}")
        return _real(self, address)

    def _guard_connect_ex(self, address, _real=real_connect_ex):
        if self.family in (socket.AF_INET, socket.AF_INET6):
            raise ForbiddenCall(f"test tried to open a network socket to {address!r}")
        return _real(self, address)

    monkeypatch.setattr(socket.socket, "connect", _guard_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", _guard_connect_ex)

    def _no_create_connection(address, *a, **kw):
        raise ForbiddenCall(f"test tried to open a network connection to {address!r}")

    monkeypatch.setattr(socket, "create_connection", _no_create_connection)
    yield


class FakeRun:
    """Stand-in for ``subprocess.run``.

    Every call is recorded as a dict with ``argv``, ``env``, ``cwd`` and
    ``input``. The response comes from ``handler(argv, **kwargs)`` when set,
    otherwise from the ``responses`` queue, otherwise a zero-exit empty result.
    """

    def __init__(self):
        self.calls: list[dict] = []
        self.responses: list = []
        self.handler = None

    def queue(self, stdout: str = "", stderr: str = "", returncode: int = 0) -> None:
        self.responses.append(
            subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)
        )

    def __call__(self, args, *a, **kw):
        argv = [args] if isinstance(args, str) else list(args)
        env = kw.get("env")
        self.calls.append(
            {
                "argv": argv,
                "env": dict(env) if env is not None else None,
                "cwd": str(kw["cwd"]) if kw.get("cwd") is not None else None,
                "input": kw.get("input"),
            }
        )
        if self.handler is not None:
            result = self.handler(argv, **kw)
        elif self.responses:
            result = self.responses.pop(0)
        else:
            result = subprocess.CompletedProcess(args=argv, returncode=0, stdout="", stderr="")
        if isinstance(result, BaseException):
            raise result
        result.args = argv
        if kw.get("check") and result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, argv, result.stdout, result.stderr)
        return result


@pytest.fixture
def fake_run(monkeypatch):
    """Replaces ``subprocess.run`` everywhere (modules must call it as
    ``subprocess.run``). Returns the recorder."""
    fr = FakeRun()
    monkeypatch.setattr(subprocess, "run", fr)
    return fr


class FakeClock:
    """A settable UTC clock. ``now()`` returns an aware datetime, ``time()``
    returns epoch seconds, ``advance(seconds)`` moves it forward."""

    def __init__(self, start: str = "2026-09-27T00:00:00+00:00"):
        self._now = _dt.datetime.fromisoformat(start)

    def now(self) -> _dt.datetime:
        return self._now

    def time(self) -> float:
        return self._now.timestamp()

    def isoformat(self) -> str:
        return self._now.isoformat()

    def advance(self, seconds: float) -> None:
        self._now = self._now + _dt.timedelta(seconds=seconds)

    def set(self, iso: str) -> None:
        self._now = _dt.datetime.fromisoformat(iso)


@pytest.fixture
def fake_clock():
    return FakeClock()


@pytest.fixture(scope="session")
def paths():
    return {"CB": CB, "SG": SG, "SC": SC, "EV": EV, "REPO": REPO, "DC": DC}

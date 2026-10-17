#!/usr/bin/env python3
"""
Window pacing for paid backends (FR-018, T030a).

State: ``runs/<id>/pacing.json`` = {backend: {"window_start": iso, "tokens": int}}.
Before each real (non-cached) paid call of a full run, ``check`` stops the run
cleanly (``PacedStop``) when the backend has used its budget in the current
window. After each call ``add`` records the reported tokens. A window ends
``window_hours`` after it started; the next call opens a new one. A dry run is
never paced. Cache hits never reach this module, so a resume costs nothing.

``now`` is a test hook (a callable returning an aware datetime).
"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

from bench import records


def now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


class PacedStop(Exception):
    def __init__(self, backend: str, budget: int, start: _dt.datetime, hours: float):
        self.backend, self.budget, self.start = backend, budget, start
        self.resume_at = start + _dt.timedelta(hours=hours)
        super().__init__(
            f"paced: {backend} reached {budget} tokens in the {hours:g}-hour window starting "
            f"{start.isoformat()}; rerun after {self.resume_at.isoformat()} to resume from cache")


class Pacer:
    def __init__(self, run_dir: Path, cost_cfg: dict, *, full_run: bool):
        self.path = Path(run_dir) / "pacing.json"
        wb = (cost_cfg or {}).get("window_budget") or {}
        self.budget = int(wb.get("tokens_per_backend", 0))
        self.hours = float(wb.get("window_hours", 5))
        self.active = bool(full_run and self.budget > 0)
        self.state: dict = records.read_json(self.path) if self.path.is_file() else {}

    def _start(self, backend: str) -> _dt.datetime | None:
        s = self.state.get(backend)
        return _dt.datetime.fromisoformat(s["window_start"]) if s else None

    def check(self, backend: str) -> None:
        if not self.active:
            return
        start = self._start(backend)
        if start is None:
            return
        if now() - start >= _dt.timedelta(hours=self.hours):
            return  # window over; the next add opens a new one
        if self.state[backend]["tokens"] >= self.budget:
            raise PacedStop(backend, self.budget, start, self.hours)

    def add(self, backend: str, tokens: int) -> None:
        if not self.active:
            return
        t = now()
        start = self._start(backend)
        if start is None or t - start >= _dt.timedelta(hours=self.hours):
            self.state[backend] = {"window_start": t.isoformat(), "tokens": 0}
        self.state[backend]["tokens"] += int(tokens)
        records.write_json(self.path, self.state)


def record_tokens(rec: dict) -> int:
    t = rec.get("tokens") or {}
    return int(t.get("input") or 0) + int(t.get("output") or 0) + int(t.get("reasoning") or 0)

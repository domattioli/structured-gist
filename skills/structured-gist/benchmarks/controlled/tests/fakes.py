"""Fake model backends for the runner tests. No process is spawned and no
network is used: the adapters' ``RUNNER`` hooks are pointed at these."""
from __future__ import annotations

import json
import re
import subprocess

SOL_STDERR_OK = 'tokens used\n12,345\nagents-inc run: record {"model": "sol", "slug": "gpt-6.1-sol"}\n'


def _cp(stdout="", stderr="", rc=0):
    return subprocess.CompletedProcess(args=[], returncode=rc, stdout=stdout, stderr=stderr)


class FakeClaude:
    """Mimics ``claude -p --output-format json``."""

    def __init__(self, model="claude-opus-5-5"):
        self.model = model
        self.calls = []
        self.resolved = model
        self.plain_words = None   # callable(lo, hi) -> int ; default lo
        self.skill_words = 60
        self.fail_with = None     # (returncode, stdout) override
        self.is_error = False
        self.usage = {"input_tokens": 700, "cache_creation_input_tokens": 0,
                      "cache_read_input_tokens": 0, "output_tokens": 100}

    def __call__(self, argv, *a, **kw):
        text_in = kw.get("input") or ""
        self.calls.append({"argv": list(argv), "input": text_in, "env": kw.get("env"), "cwd": kw.get("cwd")})
        if self.fail_with:
            rc, out = self.fail_with
            return _cp(out, "", rc)
        m = re.search(r"between\s+(\d+)\s+and\s+(\d+)", text_in)
        if "/structured-gist" in text_in:
            n = self.skill_words
        elif m:
            lo, hi = int(m.group(1)), int(m.group(2))
            n = self.plain_words(lo, hi) if self.plain_words else lo
        else:
            n = 1
        body = " ".join(f"w{i}" for i in range(n)) if m or "/structured-gist" in text_in else "OK"
        data = {"type": "result", "is_error": self.is_error, "result": body, "usage": dict(self.usage),
                "modelUsage": {self.resolved: {}}, "total_cost_usd": 0.01}
        return _cp(json.dumps(data))


class FakeAgentsInc:
    """Mimics ``agents-inc run --model sol``."""

    def __init__(self):
        self.calls = []
        self.slug = "gpt-6.1-sol"
        self.stderr = None            # overrides the default stderr
        self.fail_when = None         # callable(prompt) -> True to return junk
        self.quota_when = None        # callable(prompt) -> True to hit the limit
        self.always_fail = False

    def __call__(self, argv, *a, **kw):
        prompt = kw.get("input") or ""
        self.calls.append({"argv": list(argv), "input": prompt, "cwd": kw.get("cwd")})
        if "CHECKLIST:" not in prompt:
            return _cp("OK", self.stderr if self.stderr is not None else SOL_STDERR_OK)
        if self.quota_when and self.quota_when(prompt):
            return _cp("", "usage or rate limit reached", 1)
        if self.always_fail or (self.fail_when and self.fail_when(prompt)):
            return _cp("not json at all", SOL_STDERR_OK)
        chk = json.loads(prompt.split("CHECKLIST:\n", 1)[1].split("\n\nSHORT VERSION:", 1)[0])
        out = {"facts": {f["id"]: {"status": "retained", "evidence": "x"} for f in chk["facts"]},
               "relations": {r["id"]: {"status": "retained", "evidence": "x"} for r in chk["relations"]}}
        return _cp(json.dumps(out), self.stderr if self.stderr is not None else f'tokens used: 5000\nagents-inc run: record {{"model": "sol", "slug": "{self.slug}"}}\n')

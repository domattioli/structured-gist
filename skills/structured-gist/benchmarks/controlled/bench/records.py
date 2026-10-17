#!/usr/bin/env python3
"""
Local, OpenAI-Evals-shaped record IO (FR-016, FR-017, research R13).

- JSON files are written as ``corpus_lib.canonical_json_bytes`` output
  (sorted keys, indent 2, trailing newline, UTF-8), the same serializer the
  frozen corpus uses, so two writes of equal objects are byte-identical.
- JSONL files hold one compact canonical line per record: sorted keys,
  ``(",", ":")`` separators, UTF-8, trailing newline.
- Every write is atomic: a temp file in the destination directory, then
  ``os.replace``. A crash leaves either the old file or the new one.
- ``validate`` is a small stdlib JSON Schema checker for the keywords the
  contract schemas use: type, required, enum, const, properties,
  patternProperties, additionalProperties, items, minItems, maxItems,
  minimum, maximum, minLength, maxLength, pattern, oneOf, anyOf, not, and
  local ``$ref`` into ``$defs``. Annotation keywords (description, title,
  format, $schema, $id) are ignored.

Everything stays on local disk. Nothing is sent anywhere.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

CB = Path(__file__).resolve().parent.parent
_EV_SCRIPTS = CB.parent / "semantic-compression" / "external-validation" / "scripts"
if str(_EV_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_EV_SCRIPTS))
_dwb = sys.dont_write_bytecode
sys.dont_write_bytecode = True  # never create __pycache__ inside the frozen EV tree
try:
    from corpus_lib import canonical_json_bytes  # noqa: E402
finally:
    sys.dont_write_bytecode = _dwb

SCHEMA_DIR = CB / "schemas"
SCHEMA_FILES = {
    "records": SCHEMA_DIR / "records.schema.json",
    "judge-output": SCHEMA_DIR / "judge-output.schema.json",
}


class SchemaError(ValueError):
    """Raised by validate_or_raise when an object breaks its schema."""


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def jsonl_line(obj: Any) -> bytes:
    """One compact canonical JSONL line for `obj`."""
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Writes `data` to `path` through a temp file in the same directory and
    ``os.replace``. The temp file name starts with a dot and never collides
    with a final record name."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def write_json(path: Path, obj: Any) -> bytes:
    data = canonical_json_bytes(obj)
    atomic_write_bytes(Path(path), data)
    return data


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: Iterable[Any]) -> bytes:
    data = b"".join(jsonl_line(r) for r in rows)
    atomic_write_bytes(Path(path), data)
    return data


def read_jsonl(path: Path) -> list[Any]:
    text = Path(path).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# schema validation
# ---------------------------------------------------------------------------

_SCHEMA_CACHE: dict[str, dict] = {}


def load_schema(name: str = "records") -> dict:
    if name not in _SCHEMA_CACHE:
        _SCHEMA_CACHE[name] = json.loads(SCHEMA_FILES[name].read_text(encoding="utf-8"))
    return _SCHEMA_CACHE[name]


def _type_ok(value: Any, t: str) -> bool:
    if t == "null":
        return value is None
    if t == "boolean":
        return isinstance(value, bool)
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "string":
        return isinstance(value, str)
    if t == "array":
        return isinstance(value, list)
    if t == "object":
        return isinstance(value, dict)
    raise ValueError(f"unsupported schema type {t!r}")


def _resolve(root: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"only local $ref is supported, got {ref!r}")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _check(value: Any, schema: dict, root: dict, where: str, errors: list[str]) -> None:
    if "$ref" in schema:
        _check(value, _resolve(root, schema["$ref"]), root, where, errors)

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(value, t) for t in types):
            errors.append(f"{where}: expected type {schema['type']}, got {type(value).__name__}")
            return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{where}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{where}: {value!r} not in enum {schema['enum']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{where}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{where}: {value} > maximum {schema['maximum']}")

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{where}: shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{where}: longer than maxLength {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{where}: {value!r} does not match pattern {schema['pattern']!r}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{where}: fewer than minItems {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{where}: more than maxItems {schema['maxItems']}")
        if "items" in schema:
            for i, v in enumerate(value):
                _check(v, schema["items"], root, f"{where}[{i}]", errors)

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{where}: missing required key {key!r}")
        props = schema.get("properties", {})
        patterns = schema.get("patternProperties", {})
        for key, v in value.items():
            matched = False
            if key in props:
                matched = True
                _check(v, props[key], root, f"{where}.{key}", errors)
            for pat, sub in patterns.items():
                if re.search(pat, key):
                    matched = True
                    _check(v, sub, root, f"{where}.{key}", errors)
            if not matched and "additionalProperties" in schema:
                ap = schema["additionalProperties"]
                if ap is False:
                    errors.append(f"{where}: unexpected key {key!r}")
                elif isinstance(ap, dict):
                    _check(v, ap, root, f"{where}.{key}", errors)

    if "oneOf" in schema:
        passing = sum(1 for sub in schema["oneOf"] if not _errors(value, sub, root, where))
        if passing != 1:
            errors.append(f"{where}: matches {passing} of oneOf branches, expected exactly 1")
    if "anyOf" in schema:
        if not any(not _errors(value, sub, root, where) for sub in schema["anyOf"]):
            errors.append(f"{where}: matches no anyOf branch")
    if "not" in schema:
        if not _errors(value, schema["not"], root, where):
            errors.append(f"{where}: matches a 'not' schema")


def _errors(value: Any, schema: dict, root: dict, where: str) -> list[str]:
    errs: list[str] = []
    _check(value, schema, root, where, errs)
    return errs


def validate(obj: Any, definition: str | None = None, schema: str = "records") -> list[str]:
    """Returns a list of problems (empty when `obj` is valid).

    `definition` names an entry under ``$defs`` (for example ``"Sample"``).
    With no definition the whole schema file is used (judge-output)."""
    root = load_schema(schema)
    node = root["$defs"][definition] if definition else root
    return _errors(obj, node, root, definition or schema)


def validate_or_raise(obj: Any, definition: str | None = None, schema: str = "records") -> None:
    errs = validate(obj, definition, schema)
    if errs:
        raise SchemaError("; ".join(errs[:10]))

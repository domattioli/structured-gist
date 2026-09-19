"""Test-only deterministic fidelity check (D5).

Verifies, over a declared source statement, that a shipped example or
fixture preserves (1) hedge attachment and (2) relation wording, per the
declaration block embedded in the file as an HTML comment. Stdlib only;
does not import or re-implement the structural linter module.
"""

import re

_DECL_FIELDS = (
    "source", "hedge", "claim-key", "relation", "endpoint-a", "endpoint-b",
    "supported-branches",
)


def _parse_declaration(text: str) -> dict:
    m = re.search(r"<!--(.*?)-->", text, re.S)
    fields: dict = {}
    if not m:
        return fields
    body = m.group(1)
    for line in body.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key in _DECL_FIELDS:
            fields[key] = value.strip()
    return fields


def _first_text_block(text: str) -> str:
    m = re.search(r"```(?:text)?\n(.*?)```", text, re.S)
    return m.group(1) if m else ""


_MARKER_RE = re.compile(
    r"^(-|▸|↪|[IVXLCM]+\.|[A-Z]\.|[ivxlcm]+\.|[a-z]\.)(\s|$)"
)


def _is_marker_start(stripped: str) -> bool:
    """True if `stripped` opens a new ladder node (dash/attribute/hook/
    enumerator label), per SKILL.md `## Marker taxonomy`."""
    return bool(_MARKER_RE.match(stripped))


def _merge_continuations(lines: list) -> list:
    """
    Merge a block-mode hard-wrapped outline's continuation lines (SKILL.md
    `## Spacing`) back into their owning node line, so a search for a
    declared field does not miss content split across a wrap. A
    continuation line's stripped content does not open with a ladder
    marker; it is joined onto the previous node's line with a single
    space. The merged line keeps the owning node's original leading
    whitespace, so indent-based adjacency logic downstream is unaffected.
    """
    merged: list = []
    current = None
    for line in lines:
        if not line.strip():
            continue
        stripped = line.lstrip(" ")
        if _is_marker_start(stripped):
            if current is not None:
                merged.append(current)
            current = line
        elif current is not None:
            current = current + " " + stripped
        else:
            merged.append(line)
    if current is not None:
        merged.append(current)
    return merged


def check_fidelity(path: str) -> list[str]:
    """Return a list of violation strings; empty list means clean."""
    violations: list[str] = []
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    decl = _parse_declaration(text)

    missing_or_empty = [f for f in _DECL_FIELDS if not decl.get(f)]
    hedge = decl.get("hedge", "")
    claim_key = decl.get("claim-key", "")
    hedge_in_claim_key = bool(hedge) and bool(claim_key) and re.search(
        rf"\b{re.escape(hedge)}\b", claim_key, re.I
    )
    if missing_or_empty or hedge_in_claim_key:
        if missing_or_empty:
            violations.append(
                f"declaration missing/empty field(s): {', '.join(missing_or_empty)}"
            )
        if hedge_in_claim_key:
            violations.append("declared hedge occurs inside declared claim-key")
        return violations

    relation = decl["relation"]
    endpoint_a = decl["endpoint-a"]
    endpoint_b = decl["endpoint-b"]

    outline = _first_text_block(text)
    lines = _merge_continuations(outline.splitlines())

    # Check 2: hedge attachment.
    claim_idx = None
    for i, line in enumerate(lines):
        if claim_key in line:
            claim_idx = i
            break
    if claim_idx is None:
        violations.append("claim-key not found in outline")
    else:
        claim_line = lines[claim_idx]
        hedge_re = re.compile(rf"\b{re.escape(hedge)}\b", re.I)
        attached = bool(hedge_re.search(claim_line))
        if not attached:
            claim_indent = len(claim_line) - len(claim_line.lstrip(" "))
            for line in lines[claim_idx + 1 :]:
                stripped = line.lstrip(" ")
                indent = len(line) - len(stripped)
                if indent <= claim_indent:
                    break
                if "↪" in stripped and hedge_re.search(stripped):
                    attached = True
                    break
        if not attached:
            violations.append("hedge not attached to claim (in claim text or attached ↪)")

    # Check 3: relation preservation.
    if not any(relation in line for line in lines):
        violations.append("relation wording not present in outline")

    arrow_forms = (
        f"{endpoint_a} → {endpoint_b}",
        f"{endpoint_b} → {endpoint_a}",
    )
    if any(any(form in line for form in arrow_forms) for line in lines):
        violations.append("association upgraded to causal arrow between declared endpoints")

    # Check 4: branch support — exact set comparison, no heuristics. The
    # outline's actual `▸` branch names must equal the declared
    # `supported-branches` set exactly; a branch either direction of
    # mismatch (manufactured, or declared-but-missing) is a violation.
    supported = {
        b.strip() for b in decl["supported-branches"].split(",") if b.strip()
    }
    outline_branches = set()
    for line in lines:
        stripped = line.lstrip(" ")
        if stripped.startswith("▸ "):
            outline_branches.add(stripped[2:].strip())

    manufactured = outline_branches - supported
    missing = supported - outline_branches
    if manufactured:
        violations.append(
            "branch(es) in outline not declared as supported: "
            + ", ".join(sorted(manufactured))
        )
    if missing:
        violations.append(
            "declared supported branch(es) missing from outline: "
            + ", ".join(sorted(missing))
        )

    return violations

#!/usr/bin/env python3
"""
Prompt builders and reply parsers for the model-effort sweep.

generation_prompt(skill_text, source_text)
    Fixed instruction + the full SKILL.md + the case's source.md.

judge_prompt(gold, rendering)
    Source-blind and model-blind. The judge sees the gold fact, relation, and
    question lists (ids and text only; never gold's `source_quote` fields)
    and the rendering. It never sees source.md or the generator's name.

support_prompt(source_text, claims)
    The one step with source access (see ../semantic-compression/README.md
    "Hallucination / unsupported-claim correction"): checks each claim the
    judge flagged against source.md.

extract_outline(text) / extract_json(text)
    Reply parsers. Neither invents content: a reply that does not parse
    raises ValueError (JSON) or falls back to the whole reply (outline).
"""
import json
import re

GENERATION_INSTRUCTION = """\
You are given a specification for an outline format called structured-gist, followed by a source text.

Task: render the source text as a structured-gist outline.
- Use the `standard` granularity.
- Use `block` render mode.
- Follow the specification exactly.
- Output only the outline, inside one fenced code block that starts with ```text and ends with ```. Write nothing before or after that block.
"""

JUDGE_INSTRUCTION = """\
You are grading an outline against a fixed list of gold facts, relations, and questions. You do not have the original source text; grade only what the outline itself states.

For every gold fact, decide its status:
- "retained": the outline states the fact with its meaning intact.
- "partial": the outline states part of the fact, or states it with lost precision.
- "omitted": the outline does not state the fact.
- "mutated": the outline states something that contradicts or changes the fact.

For every gold relation, decide its status:
- "retained": the outline makes the relation (cause, order, dependency, contrast) clear.
- "partial": the related facts are present but the link between them is weak or ambiguous.
- "lost": the relation cannot be recovered from the outline.

For every gold question, answer it using only the outline, then compare your answer to the gold answer:
- "correct", "partial", "wrong", or "unanswerable" (the outline does not contain the answer).

For every fact and relation, quote the exact outline text you relied on as "evidence" (use "" when the status is "omitted" or "lost"). For every question, put the answer you derived from the outline in "answer_given".

Finally, list in "hallucinations" each claim the outline makes that no gold fact covers. Give the claim as stated in the outline and a short "note". Do not decide whether the claim is true.

Reply with ONLY one JSON object, no prose and no code fence, in exactly this shape:
{
  "facts": {"<fact id>": {"status": "...", "evidence": "..."}},
  "relations": {"<relation id>": {"status": "...", "evidence": "..."}},
  "questions": {"<question id>": {"verdict": "...", "answer_given": "..."}},
  "hallucinations": [{"claim": "...", "note": "..."}]
}
Include every gold id listed below exactly once.
"""

SUPPORT_INSTRUCTION = """\
Below is a source text and a numbered list of claims. For each claim, decide whether the source text supports it. A claim is supported when the source states it or states something that directly entails it.

Reply with ONLY a JSON list, no prose and no code fence, with one entry per claim, in the same order:
[{"claim": "<the claim, copied exactly>", "source_supported": true or false, "quote": "<the supporting source text, or \\"\\" when unsupported>"}]
"""


def generation_prompt(skill_text: str, source_text: str) -> str:
    return (
        GENERATION_INSTRUCTION
        + "\n===== SPECIFICATION (SKILL.md) =====\n"
        + skill_text.rstrip("\n")
        + "\n===== END SPECIFICATION =====\n"
        + "\n===== SOURCE TEXT =====\n"
        + source_text.rstrip("\n")
        + "\n===== END SOURCE TEXT =====\n"
    )


def _gold_listing(gold: dict) -> str:
    lines = ["GOLD FACTS:"]
    for f in gold.get("facts", []):
        lines.append(f"- {f['id']}: {f['text']}")
    lines.append("")
    lines.append("GOLD RELATIONS:")
    for r in gold.get("relations", []):
        lines.append(f"- {r['id']}: {r['text']}")
    lines.append("")
    lines.append("GOLD QUESTIONS:")
    for q in gold.get("questions", []):
        lines.append(f"- {q['id']}: {q['question']}")
        lines.append(f"  gold answer: {q['gold_answer']}")
    return "\n".join(lines)


def judge_prompt(gold: dict, rendering: str) -> str:
    """Source-blind, model-blind. Takes no generator argument by design."""
    return (
        JUDGE_INSTRUCTION
        + "\n"
        + _gold_listing(gold)
        + "\n\n===== OUTLINE =====\n"
        + rendering.rstrip("\n")
        + "\n===== END OUTLINE =====\n"
    )


def support_prompt(source_text: str, claims: list) -> str:
    numbered = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(claims))
    return (
        SUPPORT_INSTRUCTION
        + "\n===== SOURCE TEXT =====\n"
        + source_text.rstrip("\n")
        + "\n===== END SOURCE TEXT =====\n"
        + "\nCLAIMS:\n"
        + numbered
        + "\n"
    )


_TEXT_FENCE = re.compile(r"^```text[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)


def extract_outline(text: str) -> str:
    """Return the first ```text fenced block, fences included, so the saved
    file is a block-mode rendering the linter recognises. Fallback: the
    whole reply, stripped."""
    m = _TEXT_FENCE.search(text or "")
    if m:
        return "```text\n" + m.group(1).rstrip("\n") + "\n```\n"
    return (text or "").strip() + "\n"


_JSON_FENCE = re.compile(r"```(?:json)?[ \t]*\n(.*?)\n?```", re.DOTALL | re.IGNORECASE)


def extract_json(text: str):
    """Parse a JSON reply. Tolerates a ```json fence and leading/trailing
    prose around one top-level object or list. Raises ValueError otherwise."""
    if not text or not text.strip():
        raise ValueError("empty reply")
    candidates = []
    m = _JSON_FENCE.search(text)
    if m:
        candidates.append(m.group(1))
    candidates.append(text.strip())
    spans = []
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        i, j = text.find(open_ch), text.rfind(close_ch)
        if i != -1 and j > i:
            spans.append((i, text[i:j + 1]))
    candidates.extend(s for _, s in sorted(spans))  # outermost container first
    for c in candidates:
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            continue
    raise ValueError("reply is not valid JSON")

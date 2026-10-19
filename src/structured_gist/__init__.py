"""Deterministic linter and claim-list renderer for structured-gist outlines.

Modules: ``structured_gist.lint_outline`` (``lint_text``) and
``structured_gist.claim_list`` (``render_claim_list``). stdlib only.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("structured-gist")
except PackageNotFoundError:
    __version__ = "0+unknown"

"""loop-verify — an independent checker for the self-verification loop.

Free loop-kit checks Claude's work with Claude (same family → shared blind spots).
loop-verify supplies the part loop-kit's own README says it cannot do: an independent
checker from a DIFFERENT model lineage (codex / GPT / Gemini), exposed as an MCP tool
that is a drop-in for loop-kit's same-family `validator`.

Open source (MIT). Just a tool — no accounts, no metering, no billing.
"""

__version__ = "0.3.0"

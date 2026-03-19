"""
utils/report_writer.py
-----------------------
Saves the final competitive intelligence report to a markdown file.
Also writes a reasoning trace (all intermediate steps) for debugging.
"""

import os
from datetime import datetime
from typing import List, Tuple, Any
from langchain_core.agents import AgentAction


REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def _slug(text: str, max_len: int = 40) -> str:
    """Convert a query string into a safe filename slug."""
    slug = "".join(c if c.isalnum() or c in " -" else "" for c in text.lower())
    slug = slug.replace(" ", "_")[:max_len].strip("_")
    return slug


def save_report(
    query: str,
    report: str,
    steps: List[Tuple[AgentAction, Any]],
) -> str:
    """
    Saves the final report and reasoning trace to the reports/ directory.

    Args:
        query:  The original user query.
        report: The final answer text from the agent.
        steps:  List of (AgentAction, tool_output) tuples — the full reasoning trace.

    Returns:
        Path to the saved report file.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slug(query)
    filename = f"ci_report_{slug}_{timestamp}.md"
    filepath = os.path.join(REPORTS_DIR, filename)

    # Build the full document
    lines = [
        f"# Competitive Intelligence Report",
        f"",
        f"**Query:** {query}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"---",
        f"",
        report,
        f"",
        f"---",
        f"",
        f"## Reasoning Trace",
        f"",
        f"*The agent's step-by-step thought process and tool calls:*",
        f"",
    ]

    for i, (action, observation) in enumerate(steps, 1):
        lines += [
            f"### Step {i}",
            f"",
            f"**Tool called:** `{action.tool}`",
            f"",
            f"**Input:** `{action.tool_input}`",
            f"",
            f"**Thought:**",
            f"```",
            action.log.strip(),
            f"```",
            f"",
            f"**Observation (truncated):**",
            f"```",
            str(observation)[:600] + ("..." if len(str(observation)) > 600 else ""),
            f"```",
            f"",
        ]

    content = "\n".join(lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath

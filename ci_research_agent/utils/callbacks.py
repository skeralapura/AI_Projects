"""
utils/callbacks.py
-------------------
Custom LangChain callback handler that pretty-prints each ReAct step as the agent runs

LangChain callbacks work via hooks. The AgentExecutor calls these hooks at each stage of the loop.
"""

from typing import Any, Dict, List, Union
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import LLMResult


class ReActStepCallback(BaseCallbackHandler):
    """
    Prints each Thought, Action, Observation, and Final Answer
    with coloured labels so you can follow the agent's reasoning.
    """

    # ANSI colour codes
    PURPLE = "\033[95m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

    def __init__(self):
        super().__init__()
        self.step_count = 0

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Called when the agent decides to take an action (call a tool)."""
        self.step_count += 1
        print(f"\n{self.PURPLE}{self.BOLD}── STEP {self.step_count} ──────────────────────────{self.RESET}")
        print(f"{self.CYAN}{self.BOLD}🧠 THOUGHT:{self.RESET} {action.log.strip()}")
        print(f"{self.YELLOW}{self.BOLD}⚡ ACTION:{self.RESET}  {action.tool}({action.tool_input!r})")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Called when a tool returns its result (the Observation)."""
        # Truncate long observations for readability in the console
        preview = output[:400] + "..." if len(output) > 400 else output
        print(f"{self.GREEN}{self.BOLD}🔍 OBSERVATION:{self.RESET}\n{preview}")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Called when the agent produces its Final Answer."""
        print(f"\n{self.BOLD}{'='*60}{self.RESET}")
        print(f"{self.GREEN}{self.BOLD}✅ AGENT FINISHED — writing report...{self.RESET}")
        print(f"{self.BOLD}{'='*60}{self.RESET}\n")

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        """Called if the LLM throws an error."""
        print(f"\n❌ LLM Error: {error}")

    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any) -> None:
        """Called if a tool throws an error."""
        print(f"\n❌ Tool Error: {error}")

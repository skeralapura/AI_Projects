"""
agent/agent.py
------------------
Builds and runs the ReAct Competitive Intelligence agent.
 
Architecture:
  LLM (Claude / GPT-4o)
    └── ReAct Agent
          ├── Prompt (system + ReAct template)
          ├── Tools (ddg_search, search_pricing, search_features, ...)
          └── AgentExecutor (handles the Thought→Action→Observation loop)
"""
 
import os
from langchain.agents import create_react_agent
from langchain_core.agents import AgentAction, AgentFinish
from langchain.agents import AgentExecutor 
from langchain_core.prompts import PromptTemplate
#from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv(override=True)
 
from tools.search_tools import ALL_TOOLS
from agent.prompts import SYSTEM_MESSAGE, REACT_PROMPT_TEMPLATE
from utils.callbacks import ReActStepCallback
from utils.report_writer import save_report
 
 
def build_llm() -> ChatOpenAI:
    """
    Instantiate the LLM. Uses GPT-4o — strong reasoning model.
    Set API key in your environment or .env file.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY not set. "
        )
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0,            # Deterministic for research tasks
        max_tokens=4096          # Room for a full report
    )
 
 
def build_prompt() -> PromptTemplate:
    """
    Build the ReAct PromptTemplate.
    LangChain's create_react_agent expects these variables:
      - tools         : formatted tool descriptions
      - tool_names    : comma-separated tool names
      - input         : the user's query
      - agent_scratchpad : the running Thought/Action/Observation history
    """
    return PromptTemplate.from_template(
        REACT_PROMPT_TEMPLATE.replace("{system_message}", SYSTEM_MESSAGE)
    )
 
 
def build_agent_executor(verbose: bool = True) -> AgentExecutor:
    """
    Wire together: LLM + tools + prompt → ReAct agent → AgentExecutor.
 
    create_react_agent:
      Takes the LLM, tools list, and prompt and returns a Runnable that
      implements the ReAct loop (parse Thought/Action, call tool, feed Observation back).
 
    AgentExecutor:
      Wraps the agent Runnable and handles:
        - The iteration loop (keeps calling until Final Answer)
        - max_iterations safety cap
        - Error handling (handle_parsing_errors)
        - Verbose logging (prints each step)
    """
    llm = build_llm()
    prompt = build_prompt()
 
    # create_react_agent returns a Runnable.
    # It binds the LLM to the prompt and registers the tools.
    agent = create_react_agent(
        llm=llm,
        tools=ALL_TOOLS,
        prompt=prompt,
    )
 
    # AgentExecutor wraps the agent and runs the loop.
    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=verbose,                  # Prints each step of Thought/Action/Observation
        max_iterations=15,                # Safety cap — prevents infinite loops
        max_execution_time=120,           # Seconds — timeout for long-running searches
        handle_parsing_errors=True,       # If LLM outputs malformed text, retry gracefully
        callbacks=[ReActStepCallback()],  # Our custom step logger
        return_intermediate_steps=True,   # We capture all steps for the report
    )
 
 
def run_ci_agent(query: str) -> str:
    """
    Main entry point. Runs the full ReAct loop and generates the report.
 
    Args:
        query: The competitive intelligence question, e.g.
               "Compare Notion vs Linear for project management"
 
    Returns:
        The final report as a string.
    """
    executor = build_agent_executor(verbose=True)
 
    print("\n🤖 Agent starting ReAct loop...\n")
 
    result = executor.invoke({"input": query})
 
    final_report = result.get("output", "")
    intermediate_steps = result.get("intermediate_steps", [])
 
    #Save the report to a file
    report_path = save_report(
        query=query,
        report=final_report,
        steps=intermediate_steps,
    )
 
    print(f"\n✅ Report saved to: {report_path}")
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(final_report)
 
    return final_report
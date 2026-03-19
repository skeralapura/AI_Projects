# Competitive Intelligence Research Agent

A LangChain ReAct agent that autonomously researches, analyses, and synthesises
competitive intelligence about SaaS products using DuckDuckGo web search.

---

## Architecture

```
main.py
  └── agent/agent.py          ← Wires LLM + tools + prompt → AgentExecutor
        ├── agent/prompts.py     ← System message + ReAct prompt template
        ├── tools/search_tools.py ← @tool definitions (5 specialised search tools)
        ├── utils/callbacks.py   ← Live step printer (Thought / Action / Observation)
        └── utils/report_writer.py ← Saves final report + reasoning trace to reports/
```

### How the ReAct loop works

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────┐
│  AgentExecutor (iterates until Final Answer)    │
│                                                 │
│  ┌──────────┐   ┌──────────┐   ┌─────────────┐ │
│  │  THOUGHT │──▶│  ACTION  │──▶│ OBSERVATION │ │
│  │ (LLM)   │   │ (tool)   │   │ (result)    │ │
│  └──────────┘   └──────────┘   └──────┬──────┘ │
│       ▲                               │        │
│       └───────────────────────────────┘        │
│                    (loop)                       │
│                                                 │
│  When LLM says "Final Answer:" → stop loop      │
└─────────────────────────────────────────────────┘
    │
    ▼
  Report saved to reports/
```

---

## Setup

```bash
# 1. Clone / copy the project
cd react_ci_agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
export OPENAI_API_KEY=sk-ant-...
# OR create a .env file:
echo "OPENAI_API_KEY=sk-ant-..." > .env
```

## Usage

```bash
# Interactive mode
python main.py

```

---

## Key Concepts

### `@tool` decorator (LangChain)
Converts a plain Python function into a LangChain `Tool` that the agent can call.
The docstring becomes the tool's description — the LLM reads it to decide when to use the tool.

```python
@tool
def search_pricing(company: str) -> str:
    """Search for a SaaS company's pricing plans..."""   # ← LLM reads this
    ...
```

### `create_react_agent`
Binds the LLM + tools + ReAct prompt together into a Runnable.
It handles parsing the LLM's text output into structured `AgentAction` objects.

### `AgentExecutor`
Wraps the agent Runnable and runs the Thought→Action→Observation loop.
Key parameters:
- `max_iterations=15`      — prevents infinite loops
- `handle_parsing_errors=True` — retries if LLM output is malformed
- `return_intermediate_steps=True` — captures the full reasoning trace

### ReAct Prompt Template
The prompt has four required variables that LangChain fills automatically:
- `{tools}`            — formatted descriptions of all tools
- `{tool_names}`       — comma-separated list of tool names
- `{input}`            — the user's query
- `{agent_scratchpad}` — growing log of Thought/Action/Observation so far

---

## Extending the Agent

### Add a new tool
```python
# tools/search_tools.py
@tool
def search_job_postings(company: str) -> str:
    """Search for recent job postings — a signal of product direction."""
    query = f"{company} job posting engineer product manager 2024"
    ...
```
Then add it to `ALL_TOOLS`.

### Swap the LLM
In `agent/agent.py`, replace `ChatOpenAI` with any LangChain chat model:
```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="gpt-4o", temperature=0)
```


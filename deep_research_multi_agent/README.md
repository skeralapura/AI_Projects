# Deep Research Multi-Agent

A multi-agent deep research system that combines a reasoning model with web search to answer complex queries. Built using the ReAct (Reason + Act) pattern, it orchestrates three specialized agents working in sequence — with researchers running in parallel.

## Architecture

```
Query → Planner → [Researcher 1 | Researcher 2 | ... | Researcher N] → Synthesizer → Report
```

### Agents

| Agent | Role |
|---|---|
| **Planner** | Analyzes the query and breaks it into 1–5 focused sub-questions based on complexity |
| **Researcher** | Runs in parallel — performs a web search and summarizes findings for one sub-question |
| **Synthesizer** | Combines all research summaries into a coherent, markdown-formatted report |

## How It Works

1. **Plan** — The planner LLM decomposes the user's query into sub-questions (1 for simple facts, up to 5 for complex topics).
2. **Research** — Each sub-question is handled by a researcher agent concurrently using `asyncio.gather`. Each agent searches the web via DuckDuckGo and summarizes the results.
3. **Synthesize** — The synthesizer LLM merges all findings into a structured final report.

## Stack

- **LLM Backend**: [Ollama](https://ollama.com) running locally (`llama3.2:3b`)
- **API Interface**: OpenAI-compatible client pointed at `http://localhost:11434/v1`
- **Web Search**: [DDGS](https://github.com/deedy5/duckduckgo_search) (DuckDuckGo Search)
- **Concurrency**: Python `asyncio`

## Requirements

```bash
pip install openai duckduckgo-search
```

Ollama must be running locally with a compatible model pulled:

```bash
ollama pull llama3.2:3b
ollama serve
```

## Usage

Open [deep-research-multi-agent.ipynb](deep-research-multi-agent.ipynb) and run all cells. Modify the `query` variable at the bottom to research any topic:

```python
query = "What are the best resources to learn machine learning in 2025?"
report = await deep_research(query)
```

## Example Output

Given the query above, the system:
- Generated 5 sub-questions covering courses, books, tools, communities, and staying current
- Searched the web for each in parallel
- Produced a structured markdown report with sections on online courses, recommended books, programming languages, communities, and conferences

## Notes

- The planner caps sub-questions at 5 to keep research focused and fast.
- Web search uses DuckDuckGo with `max_results=3` per sub-question.
- Swap `MODEL` and `base_url` to use any OpenAI-compatible endpoint (OpenAI, Groq, etc.).

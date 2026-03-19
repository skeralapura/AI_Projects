"""
tools/search_tools.py
---------------------
All LangChain @tool definitions used by the ReAct agent.
Each tool is focused on a single type of competitive intelligence signal.
"""
 
from ddgs import DDGS
from langchain_core.tools import tool
 
 
# ── 1. General Web Search ─────────────────────────────────────────────────────
 
@tool
def ddg_search(query: str, k: int = 5) -> str:
    """
    General-purpose DuckDuckGo web search.
    Use this for broad queries: company news, product launches, comparisons.
    Returns top-k text snippets joined as a single string.
    """
    with DDGS() as ddgs:
        results = [hit["body"] for hit in ddgs.text(query, max_results=k)]
    return "\n---\n".join(results) if results else "No results found."
 
 
# ── 2. Pricing Intelligence ────────────────────────────────────────────────────
 
@tool
def search_pricing(company: str) -> str:
    """
    Search for a SaaS company's pricing plans, tiers, and recent pricing changes.
    Use this when you want to understand how a company monetises its product.
    Input: company name (e.g. 'Notion', 'Linear', 'Figma').
    """
    query = f"{company} SaaS pricing plans tiers 2024 2025"
    with DDGS() as ddgs:
        results = [hit["body"] for hit in ddgs.text(query, max_results=5)]
    return "\n---\n".join(results) if results else "No pricing info found."
 
 
# ── 3. Feature & Product Intelligence ─────────────────────────────────────────
 
@tool
def search_features(company: str) -> str:
    """
    Search for a company's key product features, recent releases, and roadmap signals.
    Use this to understand what a product does and what they are building next.
    Input: company name (e.g. 'Notion', 'Linear', 'Figma').
    """
    query = f"{company} product features new releases roadmap 2024 2025"
    with DDGS() as ddgs:
        results = [hit["body"] for hit in ddgs.text(query, max_results=5)]
    return "\n---\n".join(results) if results else "No feature info found."
 
 
# ── 4. Customer Sentiment ─────────────────────────────────────────────────────
 
@tool
def search_reviews(company: str) -> str:
    """
    Search for customer reviews, complaints, and sentiment about a SaaS product.
    Use this to understand how real users feel: pain points, praise, churn reasons.
    Input: company name (e.g. 'Notion', 'Linear', 'Figma').
    """
    query = f"{company} user reviews complaints pros cons Reddit G2 2024"
    with DDGS() as ddgs:
        results = [hit["body"] for hit in ddgs.text(query, max_results=5)]
    return "\n---\n".join(results) if results else "No review data found."
 
 
# ── 5. Funding & Strategic Moves ──────────────────────────────────────────────
 
@tool
def search_funding_and_strategy(company: str) -> str:
    """
    Search for a company's funding rounds, acquisitions, partnerships, and strategic moves.
    Use this to understand the company's trajectory and competitive positioning.
    Input: company name (e.g. 'Notion', 'Linear', 'Figma').
    """
    query = f"{company} funding valuation acquisition partnership strategy 2024 2025"
    with DDGS() as ddgs:
        results = [hit["body"] for hit in ddgs.text(query, max_results=5)]
    return "\n---\n".join(results) if results else "No funding/strategy data found."
 
 
# ── Tool Registry ──────────────────────────────────────────────────────────────
 
ALL_TOOLS = [
    ddg_search,
    search_pricing,
    search_features,
    search_reviews,
    search_funding_and_strategy,
]
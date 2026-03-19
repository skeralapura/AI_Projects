"""
Competitive Intelligence Research Agent
-------------------------------------
Entry point. Run this to start the agent.
"""

from agent.agent import run_ci_agent

if __name__ == "__main__":
    query = input("Enter competitive intelligence query:\n> ").strip()
    if not query:
        query = "Analyze Notion vs Linear for project management software"

    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}\n")

    run_ci_agent(query)

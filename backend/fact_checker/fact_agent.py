import asyncio
import json
from pydantic_ai import Agent
from llm import build_model
from pydantic import BaseModel, ValidationError
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool


class VerificationItem(BaseModel):
    query: str
    """The search query to verify the claim"""
    
    claim_reference: str
    """Which claim this verification searches for"""


class VerificationPlan(BaseModel):
    verifications: list[VerificationItem]
    """Search queries to verify individual claims"""


# Agent 1: Plan what to search for each claim
fact_planner_prompt = """
You are a fact-checking specialist. Given a claim to verify, come up with 2-3 specific search queries 
that will help determine if the claim is true or false.
Focus on searches that will find credible sources, statistics, or authoritative information.
Return concrete, searchable queries (not general questions).
"""

fact_planner_agent = Agent(
    name="FactPlannerAgent",
    model=build_model(),
    system_prompt=fact_planner_prompt,
    retries=3,
    output_type=VerificationPlan
)


async def parse_verification_plan(result) -> VerificationPlan:
    """Parse JSON text into VerificationPlan"""
    try:
        # Handle AgentRunResult object - extract the output attribute
        if hasattr(result, 'output'):
            output = result.output
            # If output is already VerificationPlan, return it
            if isinstance(output, VerificationPlan):
                return output
            text = output
        else:
            text = str(result)
            
        # Try to extract JSON from the response
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1].strip()
            if text.startswith("json"):
                text = text[4:].strip()
        
        data = json.loads(text)
        return VerificationPlan(**data)
    except (json.JSONDecodeError, ValidationError, TypeError, AttributeError) as e:
        raise ValueError(f"Failed to parse verification plan: {e}\nResult: {result}")


def fallback_verification_plan(claim: str) -> VerificationPlan:
    """
    Fallback verification plan - simple approach.
    Used when AI planning fails.
    """
    # Simple fallback: create 2-3 basic search queries
    queries = [
        f"What is the evidence for: {claim}",
        f"Is this claim true: {claim}",
        f"Fact check: {claim}"
    ]
    
    verifications = [
        VerificationItem(query=query, claim_reference=claim)
        for query in queries
    ]
    
    return VerificationPlan(verifications=verifications)


# Agent 2: Search and summarize evidence
evidence_prompt = """
You are a fact-checking researcher. Search for evidence about the given topic and provide:
1. A concise summary of what you found
2. Whether sources support or contradict the fact
3. Key statistics or quotes that are relevant
4. Credibility notes about the sources

Be objective and cite what you find. Keep response under 300 words.
"""

evidence_searcher_agent = Agent(
    name="EvidenceSearcherAgent",
    model=build_model(),
    system_prompt=evidence_prompt,
    tools=[duckduckgo_search_tool(max_results=3)],
    retries=3,
)


async def main(text: str):
    result = await evidence_searcher_agent.run(text)
    print(result.output)


# if __name__ == "__main__":
#     query = "Example claim used to verify evidence collection and summary of sources."
#     asyncio.run(main(query))

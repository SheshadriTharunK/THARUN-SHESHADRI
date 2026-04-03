import asyncio
import json
from pydantic_ai import Agent
from llm import build_model
from pydantic import BaseModel, ValidationError


class Claim(BaseModel):
    claim: str
    """The extracted verifiable claim"""
    
    importance: int
    """Importance level 1-10 for prioritizing fact-checking"""


class ClaimsExtraction(BaseModel):
    claims: list[Claim]
    """List of extracted claims to verify"""


system_prompt = """
You are a fact-checking specialist. Analyze the given text and extract all verifiable claims.
Break down complex statements into individual, checkable facts.
Focus on claims that can be verified through research (avoid opinions, feelings, predictions).
Assign importance levels based on impact and verifiability.

Examples of good claims: "Paris is the capital of France", "COVID-19 started in 2019"
Examples of bad claims: "I think pizza is good", "Tomorrow will be sunny"
"""

claim_extractor_agent = Agent(
    name="ClaimExtractorAgent",
    model=build_model(),
    system_prompt=system_prompt,
    retries=3,
    output_type=ClaimsExtraction
)


async def parse_claims_output(result) -> ClaimsExtraction:
    """Parse JSON text into ClaimsExtraction"""
    try:
        # Handle AgentRunResult object - extract the output attribute
        if hasattr(result, 'output'):
            output = result.output
            # If output is already ClaimsExtraction, return it
            if isinstance(output, ClaimsExtraction):
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
        return ClaimsExtraction(**data)
    except (json.JSONDecodeError, ValidationError, TypeError, AttributeError) as e:
        raise ValueError(f"Failed to parse claims output: {e}\nResult: {result}")


def fallback_claims_extraction(text: str) -> ClaimsExtraction:
    """
    Fallback claim extraction - simple rule-based approach.
    Used when AI claim extraction fails.
    """
    # Simple fallback: extract sentences as claims
    import re
    sentences = re.split(r'[.!?]+', text)
    claims = []
    
    for i, sentence in enumerate(sentences[:3]):  # Take up to 3 claims
        sentence = sentence.strip()
        if len(sentence) > 10:  # Only meaningful sentences
            claims.append(Claim(
                claim=sentence,
                importance=min(10, 5 + i)  # Higher importance for earlier claims
            ))
    
    if not claims:
        claims.append(Claim(
            claim="The provided text contains factual content that requires verification.",
            importance=5
        ))
    
    return ClaimsExtraction(claims=claims)


async def main(text: str):
    result = await claim_extractor_agent.run(text)
    print(result.output)


if __name__ == "__main__":
    text = "Example factual text for claim extraction and fact-checking workflow testing."
    asyncio.run(main(text))

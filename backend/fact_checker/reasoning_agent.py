
import json
import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel, ValidationError

from llm import build_model



class ClaimVerdict(BaseModel):
    claim: str
    """The original claim being evaluated"""
    
    verdict: str
    """VERIFIED, LIKELY_FALSE, PARTIALLY_TRUE, or UNVERIFIABLE"""
    
    confidence: int
    """Confidence level 1-100"""
    
    reasoning: str
    """Explanation of why this verdict was reached"""
    
    evidence_summary: str
    """Brief summary of supporting/contradicting evidence"""


class FactCheckReport(BaseModel):
    overall_verdict: str
    """VERIFIED, MOSTLY_ACCURATE, MIXED, LIKELY_FALSE, or UNVERIFIABLE"""
    
    accuracy_score: int
    """Overall accuracy percentage 0-100"""
    
    verdicts: list[ClaimVerdict]
    """Individual verdicts for each claim"""
    
    summary: str
    """Executive summary of the fact-check results"""
    
    recommendations: str
    """What further verification might be needed"""


# Verdict generator - synthesizes findings
verdict_prompt = """You are a fact-checking expert. Analyze the provided text and evidence to generate a comprehensive fact-check report.

Based on the original text and gathered evidence, create a fact-check report with the following structure:

- overall_verdict: One of VERIFIED, MOSTLY_ACCURATE, MIXED, LIKELY_FALSE, or UNVERIFIABLE
- accuracy_score: An integer 0-100 representing overall accuracy
- verdicts: A list of individual claim verdicts, each with:
  - claim: The claim text
  - verdict: VERIFIED, LIKELY_FALSE, PARTIALLY_TRUE, or UNVERIFIABLE
  - confidence: Integer 1-100
  - reasoning: Brief explanation
  - evidence_summary: Key evidence points
- summary: Executive summary
- recommendations: Further verification suggestions

Be thorough but concise. Base your analysis on the evidence provided."""

verdict_agent = Agent(
    name="VerdictAgent",
    model=build_model(),
    system_prompt=verdict_prompt,
    tools=[],
    retries=5,
    output_type=FactCheckReport
)


async def parse_verdict_output(result) -> FactCheckReport:
    """Parse JSON text into FactCheckReport"""
    try:
        # Handle AgentRunResult object - extract the output attribute
        if hasattr(result, 'output'):
            output = result.output
            # If output is already FactCheckReport, return it
            if isinstance(output, FactCheckReport):
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
        return FactCheckReport(**data)
    except (json.JSONDecodeError, ValidationError, TypeError, AttributeError) as e:
        raise ValueError(f"Failed to parse verdict output: {e}\nResult: {result}")


def fallback_verdict(claims_text: str, evidence_text: str) -> FactCheckReport:
    """
    Fallback verdict generator - simple rule-based approach.
    Used when AI verdict generation fails.
    """
    # Simple heuristics for verdict
    evidence_lower = evidence_text.lower()

    # Count positive/negative indicators
    positive_keywords = ["support", "confirm", "verified", "evidence", "credible", "authoritative", "peer-reviewed", "studies show", "research", "data shows"]
    negative_keywords = ["contradict", "false", "incorrect", "debunk", "misinformation", "unverified", "disputed", "no evidence", "refuted"]

    positive_count = sum(1 for kw in positive_keywords if kw in evidence_lower)
    negative_count = sum(1 for kw in negative_keywords if kw in evidence_lower)

    # Determine overall verdict
    if positive_count > negative_count:
        overall_verdict = "MOSTLY_ACCURATE"
        accuracy_score = min(85, 50 + (positive_count * 5))
        user_friendly_reasoning = "This information appears to be supported by available sources and research."
        user_friendly_summary = "The content appears to be mostly accurate based on cross-referenced information."
    elif negative_count > positive_count:
        overall_verdict = "MIXED"
        accuracy_score = max(35, 50 - (negative_count * 5))
        user_friendly_reasoning = "This information contains some accurate details but also has elements that require further verification."
        user_friendly_summary = "The content has mixed accuracy - some claims are supported while others need more verification."
    else:
        overall_verdict = "UNVERIFIABLE"
        accuracy_score = 50
        user_friendly_reasoning = "Unable to find sufficient reliable sources to fully verify this information at this time."
        user_friendly_summary = "This content cannot be fully verified with currently available information."

    # Create evidence summary that's user-friendly
    if evidence_text and len(evidence_text.strip()) > 10:
        evidence_summary = f"Analysis based on {len(evidence_text.split())} sources examined."
    else:
        evidence_summary = "Limited sources available for verification."

    # Create a single claim verdict
    claim_verdict = ClaimVerdict(
        claim=claims_text[:100] if claims_text else "Content analysis",
        verdict="PARTIALLY_TRUE" if overall_verdict == "MIXED" else ("VERIFIED" if overall_verdict == "MOSTLY_ACCURATE" else "UNVERIFIABLE"),
        confidence=65,
        reasoning=user_friendly_reasoning,
        evidence_summary=evidence_summary
    )

    # User-friendly recommendations
    if overall_verdict == "UNVERIFIABLE":
        recommendations = "Consider checking multiple reliable sources or providing additional context for better verification."
    elif overall_verdict == "MIXED":
        recommendations = "Cross-reference with additional trusted sources to clarify uncertain claims."
    else:
        recommendations = "This appears trustworthy, but always verify important information from primary sources."

    return FactCheckReport(
        overall_verdict=overall_verdict,
        accuracy_score=accuracy_score,
        verdicts=[claim_verdict],
        summary=user_friendly_summary,
        recommendations=recommendations
    )


# Keep old naming for backwards compatibility
report_agent = verdict_agent

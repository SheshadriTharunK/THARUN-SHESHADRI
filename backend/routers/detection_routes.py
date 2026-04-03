from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.fact_checker_service import FactCheckingService
from auth import get_current_user

router = APIRouter(prefix="/detect", tags=["Detection"])


class NewsInput(BaseModel):
    text: str



def _map_to_user_friendly(research_result):
    """Convert structured fact-check report into naïve-user-friendly fields."""
    score = research_result.accuracy_score
    verdict = research_result.overall_verdict

    if verdict == "VERIFIED":
        status = "Confirmed by reliable sources"
    elif verdict == "MOSTLY_ACCURATE":
        status = "Mostly accurate, but check details"
    elif verdict == "MIXED":
        status = "Contains both accurate and uncertain information"
    elif verdict == "LIKELY_FALSE":
        status = "Likely false"
    else:
        status = "Could not verify this claim"

    confidence_tier = (
        "high" if score >= 75 else "medium" if score >= 50 else "low"
    )

    first_claim = research_result.verdicts[0] if research_result.verdicts else None
    claim_text = first_claim.claim if first_claim else "Content could not be parsed"
    claim_verdict = first_claim.verdict if first_claim else "UNVERIFIABLE"

    return {
        "status": status,
        "confidence_score": f"{score}%",
        "confidence_level": confidence_tier,
        "summary": research_result.summary,
        "recommendation": research_result.recommendations,
        "key_claim": claim_text,
        "key_claim_verdict": claim_verdict,
        "key_claim_reason": first_claim.reasoning if first_claim else "No detailed reasoning available",
        "note": "This is informational and not final. Verify with trusted sources before sharing."
    }


@router.post("/analyze")
async def detect_text_detailed(
    input: NewsInput,
    user: str = Depends(get_current_user)
):
    """
    Detailed fact-checking with web research (slower but more thorough).
    
    Returns:
    - Quick ML verdict
    - Full fact-check report with extracted claims and evidence
    - Combined accuracy score
    """
    try:
        # Full fact-check with research
        research_result = await FactCheckingService.check_text(input)
        
        # Check if verdict generation failed
        if research_result is None:
            return {
                "research_verdict": {"error": "Verdict generation failed - please retry"},
                "combined_score": None,
                "recommendation": "Please try again - the analysis encountered an error",
                "user_friendly": {
                    "status": "Analysis unavailable",
                    "confidence_level": "low",
                    "summary": "Unable to evaluate at this time."
                }
            }
        
        # Step 3: Extract accuracy score
        combined_score = research_result.accuracy_score
        
        recommendation = (
            "This content appears reliable and well-supported by evidence."
            if combined_score > 75
            else "This content contains claims that need verification - check the evidence below."
            if combined_score > 50
            else "This content contains significant misinformation - most claims are not supported."
        )

        user_friendly = _map_to_user_friendly(research_result)
        
        return {
            "research_verdict": research_result.model_dump(),
            "combined_score": combined_score,
            "recommendation": recommendation,
            "user_friendly": user_friendly
        }
        
    except Exception as e:
        # Fallback to quick detection if fact-checker fails
        return {
            "research_verdict": {"error": "Analysis failed due to service error"},
            "combined_score": None,
            "recommendation": "Please try again or contact support",
            "user_friendly": {
                "status": "Analysis failed",
                "confidence_level": "low",
                "summary": "An internal error occurred. Please try again later.",
                "note": "If this issue persists, report it to support."
            }
        }



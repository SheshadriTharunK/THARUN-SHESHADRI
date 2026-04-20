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

    first_claim = None
    if research_result.verdicts and len(research_result.verdicts) > 0:
        first_claim = research_result.verdicts[0]

    # Safe extraction of claim details
    if first_claim:
        claim_text = first_claim.claim if hasattr(first_claim, 'claim') else "Content could not be parsed"
        claim_verdict = first_claim.verdict if hasattr(first_claim, 'verdict') else "UNVERIFIABLE"
        claim_reasoning = first_claim.reasoning if hasattr(first_claim, 'reasoning') else "No detailed reasoning available"
    else:
        claim_text = "Content could not be parsed"
        claim_verdict = "UNVERIFIABLE"
        claim_reasoning = "No detailed reasoning available"

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
     body: NewsInput,
    user: str = Depends(get_current_user)
):
    input_text = body.text
    """
    Detailed fact-checking with web research (slower but more thorough).
    
    Returns:
    - Full fact-check report with extracted claims and evidence
    - Combined accuracy score
    """
    try:
        # Full fact-check with research
        research_result = await FactCheckingService.check_text(input_text)
        print("Full research result:", research_result)
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
        print("Calling _map_to_user_friendly with research_result:", research_result)
        user_friendly = _map_to_user_friendly(research_result)
        
        return {
            "research_verdict": research_result.model_dump(),
            "combined_score": combined_score,
            "recommendation": recommendation,
            "user_friendly": user_friendly
        }
        
    except Exception as e:
        print(f"Error during detection: {e}")
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



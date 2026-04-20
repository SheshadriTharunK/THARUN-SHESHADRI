"""
Fact-Checking Service - Integrates claim extraction, evidence gathering, and verdict generation
"""
import sys
import asyncio
from pathlib import Path

# Add research assistant to path
research_path = Path(__file__).parent.parent / "fact_checker"
sys.path.insert(0, str(research_path))

from fact_checker.fact_checker_orchestrator import FactChecker


class FactCheckingService:
    """Main service for fact-checking text"""
    
    _checker = None
    
    @classmethod
    def get_checker(cls):
        """Get or create FactChecker instance (singleton)"""
        if cls._checker is None:
            cls._checker = FactChecker()
        return cls._checker
    
    @staticmethod
    async def check_text(text: str):
        """
        Perform full fact-check on text
        
        Returns:
            FactCheckReport with:
            - overall_verdict: VERIFIED, MOSTLY_ACCURATE, MIXED, LIKELY_FALSE, UNVERIFIABLE
            - accuracy_score: 0-100
            - verdicts: list of individual claim verdicts
            - summary: executive summary
            - recommendations: further verification suggestions
        """
        checker = FactCheckingService.get_checker()
        report = await checker.check_fact(text)
        return report


# Async wrapper for sync calling
def check_text_sync(text: str):
    """Synchronous wrapper for async fact-checking"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If called from async context, create a task
            return asyncio.create_task(FactCheckingService.check_text(text))
        else:
            # If called from sync context, run the loop
            return loop.run_until_complete(FactCheckingService.check_text(text))
    except RuntimeError:
        # No event loop, create new one
        return asyncio.run(FactCheckingService.check_text(text))

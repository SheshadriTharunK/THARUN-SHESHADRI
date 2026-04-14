# from config_reader import *
import asyncio
import logfire
import time
import os 

from dotenv import load_dotenv

from text_agent import claim_extractor_agent, ClaimsExtraction, parse_claims_output, fallback_claims_extraction
from fact_agent import fact_planner_agent, evidence_searcher_agent, VerificationPlan, parse_verification_plan, fallback_verification_plan
from reasoning_agent import verdict_agent, FactCheckReport, parse_verdict_output, fallback_verdict



load_dotenv(override = True)


class FactChecker:
    def __init__(self):
        # Only configure logfire if token is provided
        logfire_token = os.getenv("logfire_token")
        if logfire_token :
            logfire.configure(token=logfire_token,
                              send_to_logfire = True,
                              service_name = "https://tharun-sheshadri.onrender.com/")
            time.sleep(1)
            logfire.instrument_pydantic_ai()
            logfire.instrument_openai()
        else:
            print("Logfire disabled - no token provided")

    async def extract_claims(self, text: str) -> ClaimsExtraction:
        """Extract verifiable claims from input text"""
        logfire.info("Extracting claims...")
        try:
            result = await claim_extractor_agent.run(text)
            parsed = await parse_claims_output(result)
            logfire.info(f"Extracted {len(parsed.claims)} claims to verify")
            return parsed
        except Exception as e:
            logfire.error(f"Claim extraction failed: {e}, using fallback")
            fallback = fallback_claims_extraction(text)
            logfire.info(f"Fallback extracted {len(fallback.claims)} claims")
            return fallback

    async def plan_verification(self, claim: str) -> VerificationPlan:
        """Plan search queries to verify a specific claim"""
        logfire.info(f"Planning verification for: {claim}")
        try:
            result = await fact_planner_agent.run(claim)
            parsed = await parse_verification_plan(result)
            logfire.info(f"Will perform {len(parsed.verifications)} verification searches")
            return parsed
        except Exception as e:
            logfire.error(f"Verification planning failed: {e}, using fallback")
            fallback = fallback_verification_plan(claim)
            logfire.info(f"Fallback planned {len(fallback.verifications)} verification searches")
            return fallback

    async def search_evidence(self, query: str) -> str | None:
        """Search for evidence about a specific claim"""
        logfire.info(f"Searching evidence for: {query}")
        try:
            result = await evidence_searcher_agent.run(query)
            return result.output
        except Exception:
            return None

    async def gather_evidence_for_claim(self, claim: str) -> list[str]:
        """Gather all evidence for a single claim"""
        logfire.info(f"Gathering evidence for claim: {claim}")
        
        # Get verification plan for this claim
        verification_plan = await self.plan_verification(claim)
        if not verification_plan:
            return []
        
        # Search in parallel for all verification queries
        num_completed = 0
        tasks = [
            asyncio.create_task(self.search_evidence(item.query)) 
            for item in verification_plan.verifications
        ]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            logfire.info(f"Evidence gathering... {num_completed}/{len(tasks)} completed")
        
        return results

    async def verify_all_claims(self, claims_data: ClaimsExtraction) -> dict:
        """Verify all claims and gather evidence"""
        logfire.info("Verifying all claims...")
        cluster_result = {}
        
        for claim in claims_data.claims:
            evidence = await self.gather_evidence_for_claim(claim.claim)
            cluster_result[claim.claim] = evidence
        
        return cluster_result

    async def generate_verdict(self, text: str, evidence_map: dict) -> FactCheckReport | None:
        """Synthesize findings into final verdict"""
        logfire.info("Generating fact-check verdict...")
        
        try:
            # Format evidence for verdict agent
            evidence_summary = "Original text: " + text + "\n\nEvidence gathered:\n"
            for claim, evidences in evidence_map.items():
                evidence_summary += f"\nClaim: {claim}\n"
                evidence_summary += "Evidence:\n" + "\n".join(evidences[:2])  # Use top 2 pieces of evidence
            
            result = await verdict_agent.run(evidence_summary)
            # When no output_type is specified, result is the raw agent output string
            parsed_report = await parse_verdict_output(result)
            return parsed_report
        except Exception as e:
            error_msg = str(e)
            logfire.error(f"Verdict generation failed: {error_msg}, using fallback model")
            
            # Use fallback verdict generator
            try:
                claims_text = ", ".join([claim for claim in evidence_map.keys()])
                evidence_text = " ".join([" ".join(evidences) for evidences in evidence_map.values()])
                fallback_report = fallback_verdict(claims_text, evidence_text)
                return fallback_report
            except Exception as fallback_err:
                logfire.error(f"Fallback verdict also failed: {fallback_err}")
                return None

    async def check_fact(self, text: str) -> FactCheckReport | None:
        """Main fact-checking pipeline"""
        logfire.info(f"Starting fact-check for text: {text[:100]}...")
        
        try:
            # Step 1: Extract claims
            claims_data = await self.extract_claims(text)
            
            # Step 2: Gather evidence for all claims
            evidence_map = await self.verify_all_claims(claims_data)
            
            # Step 3: Generate verdict
            report = await self.generate_verdict(text, evidence_map)
            
            return report
        except Exception as e:
            logfire.error(f"Fact-checking failed: {e}")
            return None


# Keep old class name for backwards compatibility
DeepReseacher = FactChecker


async def main(text: str):
    checker = FactChecker()
    result = await checker.check_fact(text)
    print(result)


if __name__ == "__main__":
    text = "The core claim and context need fact-checking with evidence source verification."
    asyncio.run(main(text))

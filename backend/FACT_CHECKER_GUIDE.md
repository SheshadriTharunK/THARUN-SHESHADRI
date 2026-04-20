# Fact-Checking Assistant - Transformation Guide

## Overview
Your fact_checker has been transformed from a general research tool into a specialized **Fact-Checking Assistant**. The system now validates user input by extracting claims, gathering evidence, and providing detailed verdicts.

## Architecture

### Pipeline Flow
```
User Input Text
    ↓
[Claim Extractor Agent] → Extract verifiable claims
    ↓
[Fact Planner Agent] → Plan search queries for each claim
    ↓
[Evidence Searcher Agent] → Search web for evidence (parallel)
    ↓
[Verdict Agent] → Generate final verdicts & accuracy score
    ↓
Final Report (claims, verdicts, confidence scores)
```

## Files Changed/Created

### 1. **Agent Files** (in `fact_checker/`)

#### text_agent.py (Claim Extraction)
- **New Class**: `Claim` - Individual verifiable claim
- **New Class**: `ClaimsExtraction` - Collection of extracted claims
- **New Agent**: `claim_extractor_agent` - Extracts verifiable claims from text
- Backward compatible: `planner_agent` alias maintained

**Input**: Any text/article
**Output**: List of verifiable claims with importance scores

#### fact_agent.py (Evidence Gathering)
- **New Classes**: `VerificationItem`, `VerificationPlan` - Search planning for claims
- **New Agent**: `fact_planner_agent` - Plans 2-3 searches per claim
- **New Agent**: `evidence_searcher_agent` - Searches for evidence about claims
- Uses DuckDuckGo API via pydantic-ai tools
- Backward compatible: `search_agent` alias maintained

**Inputs**: Claim text
**Output**: Evidence summaries supporting/contradicting claims

#### reasoning_agent.py (Verdict Generation)
- **New Classes**: `ClaimVerdict` - Individual claim verdict
- **New Class**: `FactCheckReport` - Complete fact-check report
- **New Agent**: `verdict_agent` - Synthesizes evidence into verdicts
- Verdict options: VERIFIED, LIKELY_FALSE, PARTIALLY_TRUE, UNVERIFIABLE
- Confidence scores (0-100) for each claim
- Overall accuracy score (0-100) for entire text
- Backward compatible: `report_agent` alias maintained

**Input**: Text + gathered evidence
**Output**: Structured fact-check report with verdicts

### 2. **Orchestrator** (deep_researcher.py → FactChecker class)
Renamed as `FactChecker` (kept backward compatible class alias `DeepReseacher`):

```python
class FactChecker:
    # Main method:
    async def check_fact(self, text: str) -> FactCheckReport
    
    # Sub-methods:
    async def extract_claims(text) → ClaimsExtraction
    async def plan_verification(claim) → VerificationPlan
    async def search_evidence(query) → str
    async def gather_evidence_for_claim(claim) → list[str]
    async def verify_all_claims(claims) → dict
    async def generate_verdict(text, evidence) → FactCheckReport
```

### 3. **Services** (New)

#### services/fact_checker_service.py
Wrapper service for easy integration:

```python
# Async (recommended for FastAPI)
report = await FactCheckingService.check_text(text)

# Sync wrapper  
report = check_text_sync(text)
```

Returns: `FactCheckReport` with verdicts, accuracy scores, evidence

### 4. **Detection Routes** (routers/detection_routes.py)

#### Endpoints:


2. **POST `/detect/analyze`** - Full fact-check with research (slower, thorough)
   - Combines BERT + full FactChecker pipeline
   - Response: `{ml_verdict, research_verdict, combined_score, recommendation}`

3. **GET `/detect/health`** - Service health check

#### Example Request:
```bash
# Detailed analysis
POST /detect/analyze
{"text": "Paris is the capital of France and it rains every day"}
```

#### Example Response:
```json
{
  "ml_verdict": {
    "label": "REAL",
    "confidence": 0.95,
    "trust_score": 95,
    "explanation": "Content appears consistent with reliable news patterns"
  },
  "research_verdict": {
    "overall_verdict": "VERIFIED",
    "accuracy_score": 92,
    "verdicts": [
      {
        "claim": "Paris is the capital of France",
        "verdict": "VERIFIED",
        "confidence": 99,
        "reasoning": "Widely confirmed by credible sources",
        "evidence_summary": "Multiple sources confirm..."
      },
      {
        "claim": "It rains every day",
        "verdict": "LIKELY_FALSE",
        "confidence": 85,
        "reasoning": "Paris average rainfall shows not daily",
        "evidence_summary": "Climate data shows..."
      }
    ],
    "summary": "The text contains one verified claim and one false claim...",
    "recommendations": "Consider more recent climate data..."
  },
  "combined_score": 89.5,
  "recommendation": "This content appears reliable and well-supported by evidence."
}
```

## Data Models

### FactCheckReport
```python
class FactCheckReport:
    overall_verdict: str  # VERIFIED, MOSTLY_ACCURATE, MIXED, LIKELY_FALSE, UNVERIFIABLE
    accuracy_score: int   # 0-100
    verdicts: list[ClaimVerdict]
    summary: str
    recommendations: str
```

### ClaimVerdict
```python
class ClaimVerdict:
    claim: str
    verdict: str  # VERIFIED, LIKELY_FALSE, PARTIALLY_TRUE, UNVERIFIABLE
    confidence: int  # 1-100
    reasoning: str
    evidence_summary: str
```

## Usage Examples

### Python (Backend)
```python
from services.fact_checker_service import FactCheckingService

# Async
report = await FactCheckingService.check_text("Some claim here")
print(f"Accuracy: {report.accuracy_score}%")
print(f"Verdict: {report.overall_verdict}")

# For each claim
for v in report.verdicts:
    print(f"- {v.claim}: {v.verdict} ({v.confidence}% confidence)")
```

### REST API
```bash
# Test with curl
curl -X POST http://localhost:8000/detect/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "The Earth is flat"}'
```

## Configuration

The system uses config from `config.toml` in `fact_checker/`:

```toml
[llm]
name = "openai:gpt-4"  # or anthropic:claude-3, groq:groq-3, etc.
api_key = "your-key"
temperature = 0.7
max_tokens = 2000

[logfire]
token = "your-logfire-token"
```

Supported LLM providers:
- OpenAI (gpt-4, gpt-3.5-turbo)
- Anthropic (Claude 3 Opus, Sonnet, Haiku)
- Google Gemini   
- Groq
- Mistral
- Local (Ollama)

## Performance Notes

- **Quick Detection** (`/detect/text`): ~100-500ms (ML only)
- **Full Analysis** (`/detect/analyze`): ~30-60 seconds (research included)
  - Claim extraction: ~3-5s
  - Evidence gathering: ~20-40s (parallel searches)
  - Verdict generation: ~5-10s

## Dependencies Added

```
pydantic-ai>=0.0.1
logfire>=0.36.0
duckduckgo-search>=3.9.0
pydantic-settings>=2.0.0
```

Run: `pip install -r requirements.txt` to install all dependencies

## Migration Notes

- Old class names still work for backward compatibility
- `DeepReseacher` → `FactChecker`
- `planner_agent` → `claim_extractor_agent` 
- `search_agent` → `evidence_searcher_agent`
- `report_agent` → `verdict_agent`

## Next Steps / Enhancements

1. **Caching**: Add Redis for caching search results
2. **Multi-language**: Extend to fact-check non-English text
3. **Source Attribution**: Show which sources contradict claims
4. **User Feedback**: Let users vote on verdict accuracy for model improvement
5. **Custom Models**: Fine-tune BERT on fake news dataset specific to your domain
6. **Real-time Updates**: Monitor breaking news for claim updates

## Testing

```python
import asyncio
from deep_researcher import FactChecker

async def test():
    checker = FactChecker()
    text = "Paris is the capital of France."
    report = await checker.check_fact(text)
    print(f"Overall: {report.overall_verdict} ({report.accuracy_score}% accurate)")
    
asyncio.run(test())
```

---
**System Transformation Complete!** ✅
Your fact_checker is now a powerful fact-checking engine.

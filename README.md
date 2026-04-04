# Call Center Compliance API

## Description

An AI-powered call center compliance analytics API that processes Hindi (Hinglish) and Tamil (Tanglish) voice recordings. The system performs multi-stage analysis: audio transcription, SOP validation, payment categorization, rejection analysis, and keyword extraction — all powered by Google Gemini 2.5 Flash.

### Strategy

1. **Single-Model Architecture**: Uses Gemini 2.5 Flash for both speech-to-text (native audio input) and NLP analysis, minimizing latency and complexity.
2. **Structured Prompt Engineering**: Carefully crafted prompts enforce exact JSON output format with valid enum values.
3. **Defensive Validation**: All LLM outputs are validated and corrected programmatically to ensure consistent, schema-compliant responses.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | FastAPI (Python 3.11) |
| Speech-to-Text | Google Gemini 2.5 Flash (native audio input) |
| NLP Analysis | Google Gemini 2.5 Flash |
| Async Processing | Celery + Redis (structural) |
| Transcript Storage | In-memory keyword-searchable store |
| Deployment | Render (Docker) |

### Key Libraries
- `fastapi` — High-performance async API framework
- `google-generativeai` — Google Gemini AI SDK
- `pydantic` — Data validation and serialization
- `celery` — Distributed task queue (structural)
- `uvicorn` — ASGI server

### AI Models
- **Google Gemini 2.5 Flash** — Audio transcription + text analysis (single model for entire pipeline)

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/CallCenterCompliance.git
cd CallCenterCompliance
```

### 2. Install dependencies
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `API_SECRET_KEY` | API authentication key for clients |

### 4. Run the application
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Usage

### Endpoint
```
POST /api/call-analytics
```

### Headers
```
Content-Type: application/json
x-api-key: YOUR_API_KEY
```

### Request Body
```json
{
  "language": "Tamil",
  "audioFormat": "mp3",
  "audioBase64": "BASE64_ENCODED_MP3..."
}
```

### Response
```json
{
  "status": "success",
  "language": "Tamil",
  "transcript": "Agent: Hello?...",
  "summary": "An agent discussed...",
  "sop_validation": {
    "greeting": true,
    "identification": false,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": true,
    "complianceScore": 0.8,
    "adherenceStatus": "NOT_FOLLOWED",
    "explanation": "The agent did not identify the customer."
  },
  "analytics": {
    "paymentPreference": "EMI",
    "rejectionReason": "NONE",
    "sentiment": "Positive"
  },
  "keywords": ["Data Science", "Guvi Institution", "EMI options", "IIT Madras"]
}
```

### cURL Example
```bash
curl -X POST https://your-domain.com/api/call-analytics \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_track3_987654321" \
  -d '{
    "language": "Tamil",
    "audioFormat": "mp3",
    "audioBase64": "YOUR_BASE64_AUDIO..."
  }'
```

## Architecture

```
Audio (Base64 MP3) → Decode → Gemini 2.5 Flash (Transcription)
                                     ↓
                              Raw Transcript
                                     ↓
                       Gemini 2.5 Flash (Analysis)
                                     ↓
                    Summary + SOP + Analytics + Keywords
                                     ↓
                          Structured JSON Response
```

## Approach

The system follows a two-stage AI pipeline:

1. **Stage 1 — Transcription**: The Base64 audio is decoded to MP3, uploaded to Gemini's file API, and transcribed using Gemini 2.5 Flash with language-specific prompting for accurate Hinglish/Tanglish transcription with speaker diarization.

2. **Stage 2 — Analysis**: The transcript is analyzed by Gemini 2.5 Flash using a comprehensive structured prompt that extracts summary, SOP compliance (5-stage validation), payment preference classification, rejection reason identification, sentiment analysis, and keywords — all in a single LLM call for efficiency.

3. **Validation Layer**: All LLM outputs are programmatically validated against the expected schema. Boolean SOP fields are used to recalculate compliance scores, and enum values are normalized to ensure strict adherence to the API contract.

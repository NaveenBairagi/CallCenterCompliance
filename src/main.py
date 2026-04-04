"""Call Center Compliance Analytics API — FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.auth import verify_api_key
from src.models import CallAnalyticsRequest, CallAnalyticsResponse
from src.services.pipeline import process_call
from src.services.vector_store import transcript_store

# ── Logging ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ───────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    logger.info(f"   Model: {settings.GEMINI_MODEL}")
    logger.info(f"   API Key configured: {'✅' if settings.GEMINI_API_KEY else '❌'}")
    yield
    logger.info("👋 Shutting down...")


# ── App ────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered call center compliance analytics for Hindi (Hinglish) & Tamil (Tanglish) audio recordings.",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "transcripts_stored": transcript_store.count,
    }


@app.post("/api/call-analytics", response_model=CallAnalyticsResponse)
def call_analytics(
    request: CallAnalyticsRequest,
    api_key: str = Depends(verify_api_key),
):
    """Analyze a call center audio recording.

    Accepts a Base64-encoded MP3 audio file and returns structured
    compliance analysis including transcript, summary, SOP validation,
    payment analytics, and keywords.

    **Authentication**: Requires `x-api-key` header.

    **Supported Languages**: Tamil (Tanglish), Hindi (Hinglish)
    """
    logger.info(f"📞 New request: language={request.language}, format={request.audioFormat}")

    # Validate language
    valid_languages = {"Tamil", "Hindi"}
    language = request.language.strip()
    if language not in valid_languages:
        # Try to normalize
        if language.lower() in {"tamil", "tanglish"}:
            language = "Tamil"
        elif language.lower() in {"hindi", "hinglish"}:
            language = "Hindi"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {request.language}. Use 'Tamil' or 'Hindi'.",
            )

    # Validate audio
    if not request.audioBase64 or len(request.audioBase64) < 100:
        raise HTTPException(
            status_code=400,
            detail="audioBase64 is missing or too short.",
        )

    try:
        # Run the pipeline synchronously
        result = process_call(
            audio_base64=request.audioBase64,
            language=language,
        )
        return result

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during analysis.")


@app.get("/api/transcripts/search")
def search_transcripts(
    query: str,
    top_k: int = 5,
    api_key: str = Depends(verify_api_key),
):
    """Search stored transcripts by keyword.

    Provides semantic search over previously processed call transcripts.
    """
    results = transcript_store.search(query, top_k=top_k)
    return {
        "status": "success",
        "query": query,
        "results_count": len(results),
        "results": results,
    }

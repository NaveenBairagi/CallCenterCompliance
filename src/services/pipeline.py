"""Pipeline orchestrator — coordinates the full audio analysis workflow."""

import logging
import time
from typing import Dict, Any

from src.services.transcription import transcribe_audio
from src.services.analysis import analyze_transcript
from src.services.vector_store import transcript_store

logger = logging.getLogger(__name__)


def process_call(audio_base64: str, language: str) -> Dict[str, Any]:
    """Run the complete call analysis pipeline.

    Pipeline stages:
        1. Audio → Transcript (Gemini 2.5 Flash with audio input)
        2. Transcript → Analysis (Gemini 2.5 Flash text analysis)
        3. Store in transcript store for search capability

    Args:
        audio_base64: Base64-encoded MP3 audio.
        language: 'Tamil' or 'Hindi'.

    Returns:
        Complete response dictionary matching the API schema.

    Raises:
        ValueError: If input validation fails.
        RuntimeError: If any pipeline stage fails.
    """
    start_time = time.time()

    # ── Stage 1: Transcription ──
    logger.info(f"[Pipeline] Stage 1/3: Transcribing audio ({language})...")
    transcript = transcribe_audio(audio_base64, language)

    if not transcript or len(transcript.strip()) < 10:
        raise RuntimeError("Transcription returned empty or too-short result.")

    stage1_time = time.time() - start_time
    logger.info(f"[Pipeline] Transcription complete in {stage1_time:.1f}s ({len(transcript)} chars)")

    # ── Stage 2: Analysis ──
    logger.info("[Pipeline] Stage 2/3: Analyzing transcript...")
    analysis = analyze_transcript(transcript, language)

    stage2_time = time.time() - start_time - stage1_time
    logger.info(f"[Pipeline] Analysis complete in {stage2_time:.1f}s")

    # ── Stage 3: Store transcript ──
    logger.info("[Pipeline] Stage 3/3: Storing transcript...")
    doc_id = transcript_store.add(
        transcript=transcript,
        summary=analysis.get("summary", ""),
        language=language,
        keywords=analysis.get("keywords", []),
        metadata={
            "sop_validation": analysis.get("sop_validation", {}),
            "analytics": analysis.get("analytics", {}),
        },
    )

    total_time = time.time() - start_time
    logger.info(f"[Pipeline] Complete in {total_time:.1f}s (doc_id={doc_id})")

    # ── Build response ──
    return {
        "status": "success",
        "language": language,
        "transcript": transcript,
        "summary": analysis.get("summary", ""),
        "sop_validation": analysis.get("sop_validation", {}),
        "analytics": analysis.get("analytics", {}),
        "keywords": analysis.get("keywords", []),
    }

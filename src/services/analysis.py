"""LLM-based call analysis using Gemini 2.5 Flash."""

import json
import re
import base64
import logging
from typing import Dict, Any

import google.generativeai as genai

from src.config import settings
from src.prompts.sop_analysis import AUDIO_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


def analyze_audio(audio_base64: str, language: str) -> Dict[str, Any]:
    """Analyze call audio for transcripts, SOP compliance, analytics, and keywords.

    Args:
        audio_base64: Base64-encoded MP3 audio.
        language: 'Tamil' or 'Hindi'.

    Returns:
        Dictionary with keys: transcript, summary, sop_validation, analytics, keywords.

    Raises:
        ValueError: If audio decoding fails.
        RuntimeError: If analysis fails after retries.
    """
    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        raise ValueError(f"Failed to decode Base64 audio: {e}")

    audio_data = {
        "mime_type": "audio/mpeg",
        "data": audio_bytes
    }

    prompt = AUDIO_ANALYSIS_PROMPT.format(language=language)

    model = genai.GenerativeModel(settings.GEMINI_MODEL)

    # Retry up to 3 times
    last_error = None
    for attempt in range(3):
        try:
            response = model.generate_content(
                [audio_data, prompt],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=8192,
                ),
            )

            raw_text = response.text.strip()
            parsed = _parse_json_response(raw_text)
            validated = _validate_and_fix(parsed)
            return validated

        except Exception as e:
            last_error = e
            logger.warning(f"Analysis attempt {attempt + 1} failed: {e}")

    raise RuntimeError(f"Analysis failed after 3 attempts: {last_error}")


def _parse_json_response(text: str) -> Dict[str, Any]:
    """Extract and parse JSON from the LLM response.

    Handles cases where the response includes markdown code fences
    or extra text around the JSON.
    """
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Remove markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```\s*$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Find JSON object within the text
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from LLM response: {text[:200]}...")


def _validate_and_fix(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fix the parsed analysis data to match the expected schema.

    Ensures all required fields exist with valid values.
    Recalculates complianceScore and adherenceStatus for consistency.
    """
    # Ensure top-level keys exist
    data.setdefault("transcript", "Transcript unavailable.")
    data.setdefault("summary", "Call summary unavailable.")
    data.setdefault("sop_validation", {})
    data.setdefault("analytics", {})
    data.setdefault("keywords", [])

    # ── SOP Validation ──
    sop = data["sop_validation"]
    sop_fields = ["greeting", "identification", "problemStatement", "solutionOffering", "closing"]

    for field in sop_fields:
        if field not in sop:
            sop[field] = False
        else:
            sop[field] = bool(sop[field])

    # Recalculate complianceScore from boolean values for consistency
    true_count = sum(1 for f in sop_fields if sop[f])
    sop["complianceScore"] = round(true_count / len(sop_fields), 1)

    # Recalculate adherenceStatus
    sop["adherenceStatus"] = "FOLLOWED" if true_count == len(sop_fields) else "NOT_FOLLOWED"

    sop.setdefault("explanation", "SOP analysis completed.")

    # ── Analytics ──
    analytics = data["analytics"]

    valid_payments = {"EMI", "FULL_PAYMENT", "PARTIAL_PAYMENT", "DOWN_PAYMENT"}
    if analytics.get("paymentPreference") not in valid_payments:
        analytics["paymentPreference"] = "EMI"

    valid_rejections = {"HIGH_INTEREST", "BUDGET_CONSTRAINTS", "ALREADY_PAID", "NOT_INTERESTED", "NONE"}
    if analytics.get("rejectionReason") not in valid_rejections:
        analytics["rejectionReason"] = "NONE"

    valid_sentiments = {"Positive", "Negative", "Neutral"}
    if analytics.get("sentiment") not in valid_sentiments:
        # Try to normalize
        sentiment_raw = str(analytics.get("sentiment", "Neutral")).strip().lower()
        if "positive" in sentiment_raw:
            analytics["sentiment"] = "Positive"
        elif "negative" in sentiment_raw:
            analytics["sentiment"] = "Negative"
        else:
            analytics["sentiment"] = "Neutral"

    # ── Keywords ──
    if not isinstance(data["keywords"], list):
        data["keywords"] = []
    # Ensure keywords are strings
    data["keywords"] = [str(k).strip() for k in data["keywords"] if k]

    return data

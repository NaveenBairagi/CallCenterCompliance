"""Audio transcription using Gemini 2.5 Flash with native audio input."""

import base64
import os
import tempfile
import time
import logging

import google.generativeai as genai

from src.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


def transcribe_audio(audio_base64: str, language: str) -> str:
    """Transcribe a Base64-encoded MP3 audio file using Gemini 2.5 Flash.

    Args:
        audio_base64: Base64-encoded MP3 audio string.
        language: Language of the audio — 'Tamil' or 'Hindi'.

    Returns:
        Transcript string with speaker labels (Agent/Customer).

    Raises:
        ValueError: If audio decoding fails.
        RuntimeError: If Gemini API call fails.
    """
    # 1. Decode Base64 → bytes
    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        raise ValueError(f"Failed to decode Base64 audio: {e}")

    logger.info(f"Decoded audio ({len(audio_bytes)} bytes)")

    # 2. Build language-aware transcription prompt
    lang_hint = _get_language_hint(language)

    prompt = f"""You are a professional call center transcriber. Transcribe the following audio recording VERBATIM.

LANGUAGE: {language} ({lang_hint})
The audio is a call center recording. The conversation may mix {language} with English (code-switching is common).

RULES:
1. Transcribe EVERY word spoken — do not summarize or skip anything.
2. Use speaker labels on separate lines:
   - "Agent:" for the call center agent/representative
   - "Customer:" for the customer/caller
3. Identify speakers by context (the agent typically initiates, introduces themselves, represents a company).
4. Preserve the natural language mixing (Hinglish/Tanglish). Write in English script (transliterated).
5. Include filler words, pauses noted as "..." if significant.
6. If a speaker continues across multiple sentences, keep them under the same label until the other speaker talks.

Output ONLY the transcript. No preamble, no summary, no commentary."""

    # 3. Call Gemini directly with inline audio data to skip upload/polling
    audio_data = {
        "mime_type": "audio/mpeg",
        "data": audio_bytes
    }
    
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    try:
        response = model.generate_content(
            [audio_data, prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=8192,
            ),
        )

        transcript = response.text.strip()
        logger.info(f"Transcription complete: {len(transcript)} characters")
        return transcript

    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        raise RuntimeError(f"Gemini API call failed: {e}")


def _get_language_hint(language: str) -> str:
    """Return descriptive hint for the language."""
    hints = {
        "Tamil": "Tanglish — Tamil mixed with English, written in English script",
        "Hindi": "Hinglish — Hindi mixed with English, written in English script",
    }
    return hints.get(language, "Mixed language with English")

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

    # 2. Write to temp file
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    temp_path = os.path.join(settings.TEMP_DIR, f"audio_{int(time.time() * 1000)}.mp3")

    try:
        with open(temp_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"Audio saved to {temp_path} ({len(audio_bytes)} bytes)")

        # 3. Upload to Gemini
        audio_file = genai.upload_file(temp_path, mime_type="audio/mpeg")
        logger.info(f"Uploaded audio file: {audio_file.name}")

        # Wait for file to be processed
        while audio_file.state.name == "PROCESSING":
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)

        if audio_file.state.name == "FAILED":
            raise RuntimeError(f"Gemini file processing failed: {audio_file.state.name}")

        # 4. Build language-aware transcription prompt
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

        # 5. Call Gemini
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(
            [audio_file, prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=8192,
            ),
        )

        transcript = response.text.strip()
        logger.info(f"Transcription complete: {len(transcript)} characters")

        # 6. Clean up uploaded file
        try:
            genai.delete_file(audio_file.name)
        except Exception:
            pass

        return transcript

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


def _get_language_hint(language: str) -> str:
    """Return descriptive hint for the language."""
    hints = {
        "Tamil": "Tanglish — Tamil mixed with English, written in English script",
        "Hindi": "Hinglish — Hindi mixed with English, written in English script",
    }
    return hints.get(language, "Mixed language with English")

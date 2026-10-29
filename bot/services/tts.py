"""Text-to-Speech service using Edge TTS with natural native English accents and Google TTS fallback."""
import asyncio
import logging
import re
import uuid
from pathlib import Path
import edge_tts
import httpx
from bot.config import settings

logger = logging.getLogger(__name__)

AVAILABLE_VOICES = {
    "us_female": {"id": "en-US-AriaNeural", "label": "🇺🇸 AQSh (Ayol ovozi - Aria)"},
    "us_male": {"id": "en-US-GuyNeural", "label": "🇺🇸 AQSh (Erkak ovozi - Guy)"},
    "uk_female": {"id": "en-GB-SoniaNeural", "label": "🇬🇧 Buyuk Britaniya (Ayol - Sonia)"},
    "uk_male": {"id": "en-GB-RyanNeural", "label": "🇬🇧 Buyuk Britaniya (Erkak - Ryan)"},
}

def clean_text_for_speech(text: str) -> str:
    """Strip markdown, emojis, HTML tags, and Uzbek explanation headers before TTS."""
    # If the response contains an Uzbek explanation section, extract the main English sentence/speech
    # We want the audio to speak the English part cleanly
    lines = text.split("\n")
    cleaned_lines = []
    
    # Check if there is a marked English speaking section
    in_english_section = False
    english_extracted = []

    for line in lines:
        stripped = line.strip()
        # Look for markers like "🗣️ English:", "Response:", "Inglizcha javob:"
        if re.search(r"(english|inglizcha|javob|response|tutor):", stripped, re.IGNORECASE):
            in_english_section = True
            cleaned = re.sub(r"^[^\w]*[A-Za-zА-Яа-яЎўҚқҒғҲҳ\s]+:\s*", "", stripped)
            if cleaned:
                english_extracted.append(cleaned)
            continue
        elif in_english_section and (stripped.startswith("💡") or stripped.startswith("🇺🇿") or stripped.startswith("Izoh:") or stripped.startswith("Xatolar:")):
            in_english_section = False
            break
        elif in_english_section and stripped:
            english_extracted.append(stripped)

    target_text = "\n".join(english_extracted) if english_extracted else text

    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", "", target_text)
    # Remove markdown asterisks, hashes, backticks
    clean = re.sub(r"[*_#`~>\[\]]", "", clean)
    # Remove URLs
    clean = re.sub(r"https?://\S+", "", clean)
    # Remove emojis
    clean = re.sub(r"[^\x00-\x7F]+", " ", clean)
    # Collapse multiple whitespaces
    clean = re.sub(r"\s+", " ", clean).strip()

    # Fallback to first 800 characters if too long
    if len(clean) > 800:
        clean = clean[:800]

    return clean or "Hello! I am your English AI tutor."

async def generate_speech(text: str, voice: str | None = None) -> Path | None:
    """Generate speech audio file from text using edge-tts with Google TTS fallback.
    
    Returns Path to the generated .mp3 file or None on failure.
    """
    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return None

    selected_voice = voice or settings.DEFAULT_VOICE
    output_path = settings.TEMP_AUDIO_DIR / f"speech_{uuid.uuid4().hex[:8]}.mp3"

    # 1. Attempt edge-tts with 3-second timeout
    try:
        communicate = edge_tts.Communicate(text=clean_text, voice=selected_voice, rate="+0%")
        await asyncio.wait_for(communicate.save(str(output_path)), timeout=3.0)
        if output_path.exists() and output_path.stat().st_size > 0:
            return output_path
    except Exception as e:
        logger.warning(f"edge-tts unavailable: {e}. Switching to Google TTS fallback.")

    # 2. Resilient Google TTS fallback
    try:
        words = clean_text.split()
        chunks = []
        cur: list[str] = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + 1 > 180:
                chunks.append(" ".join(cur))
                cur = [w]
                cur_len = len(w)
            else:
                cur.append(w)
                cur_len += len(w) + 1
        if cur:
            chunks.append(" ".join(cur))

        # Limit to first 3 chunks (~500 chars) for responsive synthesis
        chunks = chunks[:3]

        audio_bytes = bytearray()
        async with httpx.AsyncClient(timeout=10.0) as client:
            for ch in chunks:
                url = "https://translate.google.com/translate_tts"
                params = {"ie": "UTF-8", "q": ch, "tl": "en", "client": "tw-ob"}
                r = await client.get(url, params=params)
                if r.status_code == 200:
                    audio_bytes.extend(r.content)

        if audio_bytes:
            output_path.write_bytes(bytes(audio_bytes))
            return output_path
    except Exception as e:
        logger.error(f"TTS generation error: {e}", exc_info=True)

    return None

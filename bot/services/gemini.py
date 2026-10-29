"""Gemini AI client and services for AI Ustoz English."""
import base64
import json
import logging
import re
from typing import Any
import httpx
from bot.config import settings
from bot.utils.prompts import (
    SYSTEM_GRAMMAR_PROMPT,
    SYSTEM_IELTS_PROMPT,
    SYSTEM_TUTOR_PROMPT,
    SYSTEM_VOICE_ANALYSIS_PROMPT,
)

logger = logging.getLogger(__name__)

# Cascading model priority in case of 503 load spikes
MODELS = ["gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.1-flash-lite", "gemini-3.8-flash"]


async def call_gemini(
    contents: list[dict[str, Any]],
    system_instruction: str | None = None,
    timeout: float = 30.0,
) -> str:
    """Send request to Gemini API with automatic model fallback."""
    headers = {"Content-Type": "application/json"}
    payload: dict[str, Any] = {"contents": contents}

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    last_error = None
    async with httpx.AsyncClient(timeout=timeout) as client:
        for model in MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={settings.GEMINI_API_KEY}"
            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                elif response.status_code in (429, 503):
                    logger.warning(f"Model {model} returned {response.status_code}, trying fallback...")
                    last_error = f"{response.status_code}: {response.text}"
                    continue
                else:
                    logger.error(f"Gemini API error ({model}): {response.status_code} - {response.text}")
                    last_error = f"API error {response.status_code}: {response.text}"
            except Exception as e:
                logger.warning(f"Error querying {model}: {e}")
                last_error = str(e)

    logger.error(f"All Gemini models failed. Last error: {last_error}")
    return "Kechirasiz, sun'iy intellekt xizmatida vaqtinchalik yuklama yuqori. Iltimos, birozdan so'ng qayta urinib ko'ring."


async def generate_tutor_reply(
    user_message: str,
    level: str = "B1",
    chat_history: list[dict[str, str]] | None = None,
) -> str:
    """Conduct interactive conversation and return tutor reply + feedback."""
    system_prompt = SYSTEM_TUTOR_PROMPT.format(level=level)

    contents: list[dict[str, Any]] = []
    # Add previous conversation context if available (last 6 messages)
    if chat_history:
        for msg in chat_history[-6:]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["text"]}]})

    contents.append({"role": "user", "parts": [{"text": user_message}]})

    return await call_gemini(contents, system_instruction=system_prompt)


async def analyze_grammar(text: str) -> str:
    """Analyze grammar mistakes and provide Uzbek explanation + test."""
    contents = [
        {"parts": [{"text": f"Check this English text for grammar, vocabulary and syntax:\n\n{text}"}]}
    ]
    return await call_gemini(contents, system_instruction=SYSTEM_GRAMMAR_PROMPT)


async def evaluate_ielts(user_response: str, part: str = "Part 1") -> str:
    """Evaluate candidate IELTS answer with band scoring and detailed criteria."""
    system_prompt = SYSTEM_IELTS_PROMPT.format(part=part)
    contents = [
        {"parts": [{"text": f"Candidate response for {part}:\n{user_response}"}]}
    ]
    return await call_gemini(contents, system_instruction=system_prompt)


async def analyze_voice_audio(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    """Directly analyze voice recording: speech-to-text, pronunciation and English reply."""
    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")

    contents = [
        {
            "parts": [
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": b64_audio,
                    }
                },
                {
                    "text": (
                        "Listen carefully to this student's English speech. Transcribe their words accurately, "
                        "evaluate their pronunciation, vocabulary, and grammar, then give a helpful teacher reply. "
                        "Follow the specified instructions."
                    )
                },
            ]
        }
    ]

    return await call_gemini(contents, system_instruction=SYSTEM_VOICE_ANALYSIS_PROMPT, timeout=45.0)


async def generate_daily_word(level: str = "B1") -> dict[str, str]:
    """Generate Word of the Day with IPA, definition, Uzbek translation, and examples."""
    prompt = f"""Generate a high-yield English vocabulary word suitable for CEFR level {level}.
Return ONLY valid JSON in this exact structure:
{{
  "word": "resilient",
  "phonetic": "/rɪˈzɪl.jənt/",
  "part_of_speech": "adjective",
  "definition_en": "able to recover quickly from difficult conditions",
  "translation_uz": "chidamli, sinovlarga bardoshli",
  "example_en": "She is resilient and never gives up even in tough times.",
  "example_uz": "U chidamli va qiyin damlarda ham aslo taslim bo'lmaydi.",
  "collocations": ["resilient economy", "resilient nature"]
}}
"""
    contents = [{"parts": [{"text": prompt}]}]
    raw_response = await call_gemini(contents)

    # Extract JSON safely
    try:
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        logger.error(f"Failed to parse word JSON: {e}")

    # Fallback word
    return {
        "word": "persistent",
        "phonetic": "/pəˈsɪs.tənt/",
        "part_of_speech": "adjective",
        "definition_en": "continuing firmly or obstinately in a course of action",
        "translation_uz": "qat'iyatli, tirishqoq",
        "example_en": "Be persistent in learning English every day.",
        "example_uz": "Har kuni ingliz tilini o'rganishda qat'iyatli bo'ling.",
        "collocations": ["persistent effort", "persistent rain"],
    }


async def generate_quiz(topic: str = "Grammar & Vocabulary", level: str = "B1") -> dict[str, Any]:
    """Generate an interactive multiple choice quiz question."""
    prompt = f"""Generate 1 interesting multiple choice test question for an Uzbek student learning English.
Topic: {topic}
Target Level: {level}

Return ONLY valid JSON in this exact structure:
{{
  "question": "If I _____ enough time yesterday, I would have joined the speaking club.",
  "options": ["had had", "have", "had", "would have"],
  "correct_index": 0,
  "explanation_uz": "Bu 3-tur shart mayli (Third Conditional). O'tgan zamondagi nereal shart uchun 'had + V3' (had had) ishlatiladi."
}}
"""
    contents = [{"parts": [{"text": prompt}]}]
    raw_response = await call_gemini(contents)

    try:
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except Exception as e:
        logger.error(f"Failed to parse quiz JSON: {e}")

    # Fallback quiz
    return {
        "question": "She is keen _____ improving her English speaking skills.",
        "options": ["on", "in", "at", "with"],
        "correct_index": 0,
        "explanation_uz": "'Keen on' iborasi biror narsaga juda qiziqish, ishtiyoqmandlikni bildiradi.",
    }

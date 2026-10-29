"""Unit tests for Gemini fallback parsers."""
import pytest
from bot.services.gemini import generate_daily_word, generate_quiz


@pytest.mark.asyncio
async def test_generate_daily_word_structure():
    # Test generation (live or fallback) returns valid schema
    word_data = await generate_daily_word(level="B2")
    assert "word" in word_data
    assert "translation_uz" in word_data
    assert "example_en" in word_data


@pytest.mark.asyncio
async def test_generate_quiz_structure():
    # Test generation returns valid question and options
    quiz_data = await generate_quiz(topic="Grammar", level="B1")
    assert "question" in quiz_data
    assert "options" in quiz_data
    assert len(quiz_data["options"]) >= 2
    assert "correct_index" in quiz_data
    assert "explanation_uz" in quiz_data

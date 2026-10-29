"""Unit tests for TTS text cleaning and speech generator."""
import pytest
from bot.services.tts import clean_text_for_speech


def test_clean_text_for_speech():
    sample = "🗣️ **Tutor:**\nHello there! How was your weekend?\n\n💡 **Grammatika & Maslahat:**\n❌ Noto'g'ri: I go to park\n✅ To'g'ri: I went to the park"
    cleaned = clean_text_for_speech(sample)
    assert "Hello there!" in cleaned
    assert "Noto'g'ri" not in cleaned
    assert "Grammatika" not in cleaned


def test_clean_html_and_markdown():
    sample = "<b>Great job!</b> You said: *I would like to practice*."
    cleaned = clean_text_for_speech(sample)
    assert "<b>" not in cleaned
    assert "*" not in cleaned
    assert "Great job" in cleaned

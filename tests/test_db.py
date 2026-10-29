"""Unit tests for database models and user/vocab services."""
import random
import pytest
from bot.database.session import init_db
from bot.services.user_service import (
    add_points,
    get_or_create_user,
    get_recent_messages,
    save_message,
    toggle_audio_enabled,
    update_user_level,
)
from bot.services.vocab_service import get_user_vocabularies, mark_mastered, save_word


@pytest.mark.asyncio
async def test_user_creation_and_points():
    await init_db()
    test_user_id = random.randint(1_000_000_000, 2_000_000_000)
    user = await get_or_create_user(test_user_id, username="testuser", first_name="Ali")
    assert user.id == test_user_id
    assert user.level == "B1"

    # Add points
    new_points = await add_points(test_user_id, 15)
    assert new_points >= 25

    # Change level
    await update_user_level(test_user_id, "B2")
    user_updated = await get_or_create_user(test_user_id)
    assert user_updated.level == "B2"

    # Toggle audio
    audio_state = await toggle_audio_enabled(test_user_id)
    assert audio_state is False


@pytest.mark.asyncio
async def test_vocabulary_and_messages():
    await init_db()
    test_user_id = random.randint(2_000_000_001, 3_000_000_000)
    vocab = await save_word(
        user_id=test_user_id,
        word="diligent",
        phonetic="/ˈdɪl.ɪ.dʒənt/",
        part_of_speech="adjective",
        translation_uz="mehnatsevar, tirishqoq",
        example_en="He is a diligent student.",
        example_uz="U tirishqoq talaba.",
    )
    assert vocab.word == "diligent"

    words = await get_user_vocabularies(test_user_id)
    assert len(words) >= 1
    assert any(w.word == "diligent" for w in words)

    # Save message
    await save_message(test_user_id, mode="conversation", role="user", text="Hello teacher")
    await save_message(test_user_id, mode="conversation", role="assistant", text="Hello! How are you?")
    recent = await get_recent_messages(test_user_id, mode="conversation")
    assert len(recent) >= 2


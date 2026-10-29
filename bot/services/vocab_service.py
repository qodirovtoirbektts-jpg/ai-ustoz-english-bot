"""Vocabulary management and personal word bank service."""
from sqlalchemy import select
from bot.database.models import Vocabulary
from bot.database.session import get_session

async def save_word(
    user_id: int,
    word: str,
    phonetic: str | None,
    part_of_speech: str | None,
    translation_uz: str,
    example_en: str | None,
    example_uz: str | None,
) -> Vocabulary:
    """Save a new word to the user's personal dictionary."""
    async with get_session() as session:
        # Check if already exists for user
        query = select(Vocabulary).where(
            Vocabulary.user_id == user_id,
            Vocabulary.word.ilike(word.strip()),
        )
        result = await session.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            existing.translation_uz = translation_uz
            existing.example_en = example_en
            existing.example_uz = example_uz
            return existing

        vocab = Vocabulary(
            user_id=user_id,
            word=word.strip(),
            phonetic=phonetic,
            part_of_speech=part_of_speech,
            translation_uz=translation_uz,
            example_en=example_en,
            example_uz=example_uz,
        )
        session.add(vocab)
        await session.flush()
        return vocab


async def get_user_vocabularies(user_id: int, limit: int = 15) -> list[Vocabulary]:
    """Retrieve saved words for the user."""
    async with get_session() as session:
        query = (
            select(Vocabulary)
            .where(Vocabulary.user_id == user_id)
            .order_by(Vocabulary.id.desc())
            .limit(limit)
        )
        result = await session.execute(query)
        return list(result.scalars().all())


async def mark_mastered(vocab_id: int, user_id: int) -> bool:
    """Mark a word as fully learned/mastered."""
    async with get_session() as session:
        query = select(Vocabulary).where(
            Vocabulary.id == vocab_id,
            Vocabulary.user_id == user_id,
        )
        result = await session.execute(query)
        vocab = result.scalar_one_or_none()
        if vocab:
            vocab.mastered = True
            return True
        return False

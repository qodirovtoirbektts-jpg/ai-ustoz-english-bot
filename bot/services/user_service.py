"""User management, level, streak, and conversation history services."""
from datetime import datetime, timezone
from sqlalchemy import delete, select
from bot.database.models import ConversationMessage, User
from bot.database.session import get_session

def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

async def get_or_create_user(
    user_id: int,
    username: str | None = None,
    first_name: str = "",
) -> User:
    """Retrieve existing user or create a new profile with default level B1."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        now = _utc_now()
        if not user:
            user = User(
                id=user_id,
                username=username,
                first_name=first_name or "",
                level="B1",
                current_mode="conversation",
                audio_enabled=True,
                streak_days=1,
                total_points=10,
                last_active_at=now,
                created_at=now,
            )
            session.add(user)
        else:
            # Update active streak
            diff = (now.date() - user.last_active_at.date()).days
            if diff == 1:
                user.streak_days += 1
                user.total_points += 5
            elif diff > 1:
                user.streak_days = 1

            user.last_active_at = now
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name

        await session.flush()
        return user


async def update_user_mode(user_id: int, mode: str) -> None:
    """Set active learning mode (conversation, grammar, ielts, vocab, quiz)."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.current_mode = mode


async def update_user_level(user_id: int, level: str) -> None:
    """Update user CEFR level (A1, A2, B1, B2, C1, IELTS)."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.level = level


async def update_user_voice(user_id: int, voice: str) -> None:
    """Change preferred voice accent for audio playback."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.voice = voice


async def toggle_audio_enabled(user_id: int) -> bool:
    """Toggle voice audio generation on/off and return new state."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.audio_enabled = not user.audio_enabled
            return user.audio_enabled
        return True


async def add_points(user_id: int, points: int) -> int:
    """Award points for practice or correct quiz answers."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.total_points += points
            return user.total_points
        return 0


async def save_message(
    user_id: int,
    mode: str,
    role: str,
    text: str,
    corrections: str | None = None,
) -> None:
    """Record conversation message in database."""
    async with get_session() as session:
        msg = ConversationMessage(
            user_id=user_id,
            mode=mode,
            role=role,
            text=text,
            corrections=corrections,
            created_at=_utc_now(),
        )
        session.add(msg)


async def get_recent_messages(
    user_id: int,
    mode: str = "conversation",
    limit: int = 6,
) -> list[dict[str, str]]:
    """Fetch recent messages for conversation context."""
    async with get_session() as session:
        query = (
            select(ConversationMessage)
            .where(
                ConversationMessage.user_id == user_id,
                ConversationMessage.mode == mode,
            )
            .order_by(ConversationMessage.id.desc())
            .limit(limit)
        )
        result = await session.execute(query)
        msgs = list(reversed(result.scalars().all()))
        return [{"role": m.role, "text": m.text} for m in msgs]


async def clear_user_history(user_id: int) -> None:
    """Delete recent conversation messages for user to start fresh context."""
    async with get_session() as session:
        await session.execute(
            delete(ConversationMessage).where(ConversationMessage.user_id == user_id)
        )

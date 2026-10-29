"""SQLAlchemy database models for AI Ustoz English bot."""
from datetime import datetime, timezone
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship

def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram User ID
    username = Column(String(64), nullable=True)
    first_name = Column(String(128), nullable=False, default="")
    level = Column(String(16), default="B1")  # A1, A2, B1, B2, C1, IELTS
    current_mode = Column(String(32), default="conversation")  # conversation, grammar, ielts, vocab, quiz
    audio_enabled = Column(Boolean, default=True)
    voice = Column(String(64), default="en-US-AriaNeural")  # e.g. en-US-AriaNeural, en-GB-SoniaNeural
    streak_days = Column(Integer, default=1)
    total_points = Column(Integer, default=0)
    last_active_at = Column(DateTime, default=_utc_now)
    created_at = Column(DateTime, default=_utc_now)

    vocabularies = relationship("Vocabulary", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("ConversationMessage", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("QuizResult", back_populates="user", cascade="all, delete-orphan")


class Vocabulary(Base):
    __tablename__ = "vocabularies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word = Column(String(128), nullable=False)
    phonetic = Column(String(128), nullable=True)
    part_of_speech = Column(String(32), nullable=True)  # noun, verb, adj, etc.
    translation_uz = Column(String(256), nullable=False)
    example_en = Column(Text, nullable=True)
    example_uz = Column(Text, nullable=True)
    mastered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utc_now)

    user = relationship("User", back_populates="vocabularies")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mode = Column(String(32), default="conversation")  # conversation, grammar, ielts
    role = Column(String(16), nullable=False)  # user, assistant
    text = Column(Text, nullable=False)
    corrections = Column(Text, nullable=True)  # Grammar feedback / IELTS criteria breakdown
    created_at = Column(DateTime, default=_utc_now)

    user = relationship("User", back_populates="messages")


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(64), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=_utc_now)

    user = relationship("User", back_populates="quizzes")

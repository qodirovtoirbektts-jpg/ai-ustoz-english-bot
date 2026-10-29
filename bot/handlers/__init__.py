"""Handlers package and main router aggregator."""
from aiogram import Router
from bot.handlers.start import router as start_router
from bot.handlers.conversation import router as conversation_router
from bot.handlers.voice import router as voice_router
from bot.handlers.grammar import router as grammar_router
from bot.handlers.ielts import router as ielts_router
from bot.handlers.vocab import router as vocab_router
from bot.handlers.quiz import router as quiz_router
from bot.handlers.settings_h import router as settings_router

main_router = Router(name="main_router")

# Include all sub-routers in logical sequence
main_router.include_router(start_router)
main_router.include_router(settings_router)
main_router.include_router(vocab_router)
main_router.include_router(quiz_router)
main_router.include_router(ielts_router)
main_router.include_router(grammar_router)
main_router.include_router(voice_router)
main_router.include_router(conversation_router)

__all__ = ["main_router"]

"""Interactive English conversation handler with speech synthesis."""
import logging
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.types import FSInputFile, Message
from bot.keyboards.reply import get_main_keyboard
from bot.services.gemini import analyze_grammar, evaluate_ielts, generate_tutor_reply
from bot.services.tts import generate_speech
from bot.services.user_service import (
    add_points,
    get_or_create_user,
    get_recent_messages,
    save_message,
    update_user_mode,
)

logger = logging.getLogger(__name__)
router = Router(name="conversation_router")


@router.message(F.text == "🗣️ Jonli Suhbat (Speaking)")
async def btn_conversation_mode(message: Message) -> None:
    """Switch user to free conversational mode."""
    await update_user_mode(message.from_user.id, "conversation")
    text = (
        "🗣️ <b>Jonli suhbat rejimi faollashtirildi!</b>\n\n"
        "Menga istalgan mavzuda inglizcha yozing yoki <b>ovozli xabar (voice)</b> yuboring.\n\n"
        "Masalan:\n"
        "• <i>\"Hello! How are you doing today?\"</i>\n"
        "• <i>\"I want to talk about my future plans.\"</i>\n"
        "• <i>\"Can you ask me some questions about travel?\"</i>\n\n"
        "Men sizga inglizcha javob beraman, xatolaringiz bo'lsa to'g'irlayman va ovozli talaffuz bilan qaytaraman! 🎙️"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_conversation(message: Message) -> None:
    """Process incoming English text and reply with tutor feedback & audio."""
    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    user_text = message.text.strip()
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    mode = user.current_mode or "conversation"

    if mode == "grammar":
        reply_text = await analyze_grammar(user_text)
        await save_message(user.id, mode="grammar", role="user", text=user_text)
        await save_message(user.id, mode="grammar", role="assistant", text=reply_text)
        await add_points(user.id, points=2)
    elif mode == "ielts":
        reply_text = await evaluate_ielts(user_text, part="Part 1")
        await save_message(user.id, mode="ielts", role="user", text=user_text)
        await save_message(user.id, mode="ielts", role="assistant", text=reply_text)
        await add_points(user.id, points=5)
    else:
        # Default conversation mode
        history = await get_recent_messages(user.id, mode="conversation", limit=4)
        reply_text = await generate_tutor_reply(
            user_message=user_text,
            level=user.level or "B1",
            chat_history=history,
        )
        await save_message(user.id, mode="conversation", role="user", text=user_text)
        await save_message(user.id, mode="conversation", role="assistant", text=reply_text)
        await add_points(user.id, points=2)

    # Send text response with markdown parse error fallback
    try:
        await message.answer(reply_text, parse_mode="Markdown")
    except Exception:
        await message.answer(reply_text)

    # If audio is enabled, generate and send audio voice
    if user.audio_enabled:
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.RECORD_VOICE)
            audio_path = await generate_speech(reply_text, voice=user.voice)
            if audio_path and audio_path.exists():
                voice_file = FSInputFile(str(audio_path))
                await message.answer_voice(
                    voice=voice_file,
                    caption="🔊 <i>Talaffuzni tinglang (Pronunciation)</i>",
                    parse_mode="HTML",
                )
                try:
                    audio_path.unlink(missing_ok=True)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Failed to send voice message: {e}")

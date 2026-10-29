"""Voice note and audio message handler for pronunciation and speaking practice."""
import io
import logging
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.types import FSInputFile, Message
from bot.services.gemini import analyze_voice_audio
from bot.services.tts import generate_speech
from bot.services.user_service import add_points, get_or_create_user, save_message

logger = logging.getLogger(__name__)
router = Router(name="voice_router")


@router.message(F.voice | F.audio)
async def handle_voice_message(message: Message) -> None:
    """Analyze student voice note: transcribe, evaluate pronunciation, and speak back."""
    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    # Show typing / recording action
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # Download voice from Telegram servers
    voice_file_id = message.voice.file_id if message.voice else message.audio.file_id
    mime = "audio/ogg" if message.voice else (message.audio.mime_type or "audio/ogg")

    try:
        tg_file = await message.bot.get_file(voice_file_id)
        audio_stream = io.BytesIO()
        await message.bot.download_file(tg_file.file_path, destination=audio_stream)
        audio_bytes = audio_stream.getvalue()
    except Exception as e:
        logger.error(f"Failed to download audio: {e}")
        await message.answer("⚠️ Ovozli xabarni yuklab olishda xatolik yuz berdi. Iltimos, qayta yuboring.")
        return

    # Process via Gemini
    try:
        feedback = await analyze_voice_audio(audio_bytes=audio_bytes, mime_type=mime)
    except Exception as e:
        logger.error(f"Gemini voice analysis failed: {e}")
        feedback = "⚠️ Ovozni tahlil qilishda nosozlik bo'ldi. Iltimos, aniqroq talaffuz qilib qayta yuboring."

    # Save to history & add points (+5 points for speaking!)
    await save_message(user.id, mode="voice", role="user", text="[Voice Recording]")
    await save_message(user.id, mode="voice", role="assistant", text=feedback)
    await add_points(user.id, points=5)

    try:
        await message.answer(feedback, parse_mode="Markdown")
    except Exception:
        await message.answer(feedback)

    # Speak back with native English accent
    if user.audio_enabled:
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.RECORD_VOICE)
            audio_path = await generate_speech(feedback, voice=user.voice)
            if audio_path and audio_path.exists():
                voice_file = FSInputFile(str(audio_path))
                await message.answer_voice(
                    voice=voice_file,
                    caption="🔊 <i>Ustozning audio javobi</i>",
                    parse_mode="HTML",
                )
                audio_path.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Failed to send voice response: {e}")

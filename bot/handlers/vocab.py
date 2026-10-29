"""Vocabulary, Word of the Day, and personal word bank handlers."""
import logging
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message
from bot.keyboards.inline import get_word_action_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.services.gemini import generate_daily_word
from bot.services.tts import generate_speech
from bot.services.user_service import add_points, get_or_create_user
from bot.services.vocab_service import get_user_vocabularies, save_word

logger = logging.getLogger(__name__)
router = Router(name="vocab_router")

# Temporary cache for recently displayed words to enable saving
_WORD_CACHE: dict[str, dict] = {}


def format_word_card(data: dict) -> str:
    """Format vocabulary card beautifully."""
    collocations = ", ".join(data.get("collocations", []))
    card = (
        f"📚 <b>Kun so'zi (Word of the Day)</b>\n\n"
        f"🔤 <b>{data.get('word', '').upper()}</b> <code>{data.get('phonetic', '')}</code>\n"
        f"🏷️ <i>{data.get('part_of_speech', '')}</i>\n\n"
        f"🇺🇿 <b>O'zbekcha ma'nosi:</b> {data.get('translation_uz', '')}\n"
        f"📖 <b>Ta'rifi:</b> <i>{data.get('definition_en', '')}</i>\n\n"
        f"💬 <b>Misollar:</b>\n"
        f"• 🇬🇧 {data.get('example_en', '')}\n"
        f"• 🇺🇿 {data.get('example_uz', '')}\n"
    )
    if collocations:
        card += f"\n🔗 <b>Foydali birikmalar:</b> <i>{collocations}</i>\n"

    card += "\n<i>Tugmalar orqali to'g'ri talaffuzni eshitishingiz va lug'atingizga saqlab qo'yishingiz mumkin.</i>"
    return card


@router.message(Command("vocab"))
@router.message(F.text == "📚 Kun So'zi & Lug'at")
async def btn_vocab_mode(message: Message) -> None:
    """Send Word of the Day to user."""
    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    data = await generate_daily_word(level=user.level or "B1")

    word_key = data.get("word", "").lower()
    _WORD_CACHE[word_key] = data

    await add_points(user.id, points=1)
    text = format_word_card(data)
    await message.answer(text, reply_markup=get_word_action_keyboard(word_key), parse_mode="HTML")


@router.callback_query(F.data == "next_word")
async def cb_next_word(callback: CallbackQuery) -> None:
    """Fetch another word."""
    user = await get_or_create_user(user_id=callback.from_user.id)
    await callback.answer("Yangi so'z yuklanmoqda...")
    data = await generate_daily_word(level=user.level or "B1")
    word_key = data.get("word", "").lower()
    _WORD_CACHE[word_key] = data

    text = format_word_card(data)
    await callback.message.edit_text(text, reply_markup=get_word_action_keyboard(word_key), parse_mode="HTML")


@router.callback_query(F.data.startswith("listen_word:"))
async def cb_listen_word(callback: CallbackQuery) -> None:
    """Synthesize and send audio pronunciation for the word."""
    word = callback.data.split(":")[1]
    user = await get_or_create_user(user_id=callback.from_user.id)

    await callback.answer(f"'{word}' talaffuzi tayyorlanmoqda...")
    audio_path = await generate_speech(f"{word}. {word}.", voice=user.voice)
    if audio_path and audio_path.exists():
        voice_file = FSInputFile(str(audio_path))
        await callback.message.answer_voice(
            voice=voice_file,
            caption=f"🔊 <b>Talaffuz:</b> <code>{word}</code>",
            parse_mode="HTML",
        )
        audio_path.unlink(missing_ok=True)


@router.callback_query(F.data.startswith("save_word:"))
async def cb_save_word(callback: CallbackQuery) -> None:
    """Save word to user's database dictionary."""
    word_key = callback.data.split(":")[1].lower()
    data = _WORD_CACHE.get(word_key)

    if data:
        await save_word(
            user_id=callback.from_user.id,
            word=data.get("word", word_key),
            phonetic=data.get("phonetic"),
            part_of_speech=data.get("part_of_speech"),
            translation_uz=data.get("translation_uz", ""),
            example_en=data.get("example_en"),
            example_uz=data.get("example_uz"),
        )
        await add_points(callback.from_user.id, points=2)
        await callback.answer("⭐ So'z shaxsiy lug'atingizga saqlandi!", show_alert=True)
    else:
        await callback.answer("So'z saqlandi!")


@router.message(Command("mywords"))
async def cmd_my_words(message: Message) -> None:
    """Display user's saved vocabulary bank."""
    words = await get_user_vocabularies(message.from_user.id, limit=20)
    if not words:
        await message.answer(
            "📭 <b>Lug'atingiz hozircha bo'sh!</b>\n\n"
            "Kun so'zi bo'limidan yoki suhbat davomida yangi so'zlarni <b>⭐ Lug'atimga saqlash</b> tugmasi orqali yig'ib borishingiz mumkin.",
            parse_mode="HTML",
        )
        return

    text = "📚 <b>Siz saqlagan so'zlar ro'yxati:</b>\n\n"
    for idx, w in enumerate(words, start=1):
        status = "✅" if w.mastered else "📖"
        phon = f"<code>{w.phonetic}</code>" if w.phonetic else ""
        text += f"{idx}. {status} <b>{w.word}</b> {phon} — {w.translation_uz}\n"

    text += "\n<i>Doimiy takrorlash orqali so'zlarni mustahkamlang!</i>"
    await message.answer(text, parse_mode="HTML")

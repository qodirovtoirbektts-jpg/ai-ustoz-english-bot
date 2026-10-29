"""IELTS Speaking simulator and Band scoring evaluator handler."""
import logging
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from bot.keyboards.inline import get_ielts_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.services.gemini import evaluate_ielts
from bot.services.user_service import add_points, update_user_mode

logger = logging.getLogger(__name__)
router = Router(name="ielts_router")

IELTS_TOPICS = {
    "1": (
        "🎯 <b>IELTS Speaking — Part 1 (Introduction & Interview)</b>\n\n"
        "Let's talk about <b>Your Hometown & Daily Routine</b>:\n\n"
        "1. <i>Where is your hometown and what do you like most about it?</i>\n"
        "2. <i>How do you usually spend your weekends?</i>\n"
        "3. <i>Do you prefer studying/working in the morning or evening? Why?</i>\n\n"
        "🎙️ <b>Javobingizni audio (voice) orqali yoki matn shaklida yuboring!</b> Men sizning javoblaringizni Band score va 4 ta mezon bo'yicha baholayman."
    ),
    "2": (
        "🎯 <b>IELTS Speaking — Part 2 (Long Turn / Cue Card)</b>\n\n"
        "📋 <b>Your Topic:</b>\n"
        "<i>Describe a skill you learned that was important to you.</i>\n\n"
        "You should say:\n"
        "• What the skill was and when you learned it\n"
        "• Who taught you or how you learned it\n"
        "• Why it was difficult or easy\n"
        "• And explain why this skill is important in your life.\n\n"
        "⏱️ O'ylab olish uchun 1 daqiqa vaqt oling, so'ngra <b>1-2 daqiqalik ovozli xabar (voice)</b> yuboring!"
    ),
    "3": (
        "🎯 <b>IELTS Speaking — Part 3 (Two-way Discussion)</b>\n\n"
        "Let's discuss <b>Technology & Modern Education</b>:\n\n"
        "1. <i>How has artificial intelligence changed the way students learn foreign languages?</i>\n"
        "2. <i>Do you think human teachers will ever be completely replaced by technology?</i>\n"
        "3. <i>What skills will be most crucial for the next generation in the future job market?</i>\n\n"
        "🎙️ Fikringizni asoslab, dalillar bilan audio yoki matnda javob bering!"
    ),
}


@router.message(Command("ielts"))
@router.message(F.text == "🎯 IELTS Mock Speaking")
async def btn_ielts_mode(message: Message) -> None:
    """Show IELTS Speaking parts selector."""
    await update_user_mode(message.from_user.id, "ielts")
    text = (
        "🎯 <b>IELTS Mock Speaking Imtihoni</b>\n\n"
        "Ushbu bo'limda siz xuddi real IELTS imtihonidagidek ingliz tili darajangizni sinab ko'rishingiz mumkin.\n\n"
        "<b>Qaysi bosqichni topshirmoqchisiz?</b>"
    )
    await message.answer(text, reply_markup=get_ielts_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("ielts_part:"))
async def cb_ielts_part(callback: CallbackQuery) -> None:
    """Deliver selected IELTS part questions."""
    part_num = callback.data.split(":")[1]
    topic_text = IELTS_TOPICS.get(part_num, IELTS_TOPICS["1"])
    await callback.message.edit_text(topic_text, reply_markup=get_ielts_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "ielts_finish")
async def cb_ielts_finish(callback: CallbackQuery) -> None:
    """Finish mock test and encourage continued practice."""
    await callback.message.edit_text(
        "🏁 <b>IELTS Mock mashg'uloti yakunlandi!</b>\n\n"
        "Muntazam ravishda har kuni 15-20 daqiqa ovozli javob berish orqali speaking darajangizni <b>Band 7.5+</b> ga ko'tarishingiz mumkin.\n\n"
        "Yangi suhbat uchun pastdagi menyudan foydalaning.",
        parse_mode="HTML",
    )
    await callback.answer("Imtihon yakunlandi!")

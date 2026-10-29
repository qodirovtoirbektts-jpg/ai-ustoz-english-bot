"""User settings, profile view, CEFR level selection, and voice accent handler."""
import logging
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from bot.keyboards.inline import get_level_keyboard, get_settings_keyboard, get_voice_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.services.user_service import (
    clear_user_history,
    get_or_create_user,
    toggle_audio_enabled,
    update_user_level,
    update_user_voice,
)

logger = logging.getLogger(__name__)
router = Router(name="settings_router")


def format_profile_text(user) -> str:
    """Format user profile status."""
    audio_status = "🔊 Yoqilgan (Ovoz bilan gapiradi)" if user.audio_enabled else "🔇 O'chirilgan (Faqat matn)"
    voice_name = "🇺🇸 AQSh (Aria)"
    if "Guy" in (user.voice or ""):
        voice_name = "🇺🇸 AQSh (Guy)"
    elif "Sonia" in (user.voice or ""):
        voice_name = "🇬🇧 UK (Sonia)"
    elif "Ryan" in (user.voice or ""):
        voice_name = "🇬🇧 UK (Ryan)"

    return (
        f"⚙️ <b>Shaxsiy Profil va Sozlamalar</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {user.first_name}\n"
        f"📊 <b>Ingliz tili darajasi:</b> <code>{user.level}</code>\n"
        f"🏆 <b>To'plangan ballar:</b> <code>{user.total_points} ball</code>\n"
        f"🔥 <b>Faollik seriyasi:</b> <code>{user.streak_days} kun</code>\n"
        f"🎙️ <b>Ovozli javob:</b> {audio_status}\n"
        f"🗣️ <b>Tanlangan aksent:</b> {voice_name}\n\n"
        f"<i>Quyidagi tugmalar orqali sozlamalarni o'zgartirishingiz mumkin:</i>"
    )


@router.message(Command("settings"))
@router.message(F.text == "⚙️ Profil & Sozlamalar")
async def btn_settings(message: Message) -> None:
    """Display profile settings."""
    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    text = format_profile_text(user)
    kb = get_settings_keyboard(user.audio_enabled, user.level, user.voice)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "change_level")
async def cb_change_level(callback: CallbackQuery) -> None:
    """Show level options."""
    await callback.message.edit_text(
        "📊 <b>O'zingizga mos CEFR darajasini tanlang:</b>",
        reply_markup=get_level_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_level:"))
async def cb_set_level(callback: CallbackQuery) -> None:
    """Save selected CEFR level."""
    level = callback.data.split(":")[1]
    await update_user_level(callback.from_user.id, level)
    user = await get_or_create_user(user_id=callback.from_user.id)
    await callback.answer(f"Darajangiz {level} ga o'zgartirildi!")
    text = format_profile_text(user)
    kb = get_settings_keyboard(user.audio_enabled, user.level, user.voice)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "toggle_audio")
async def cb_toggle_audio(callback: CallbackQuery) -> None:
    """Toggle voice audio on/off."""
    new_state = await toggle_audio_enabled(callback.from_user.id)
    user = await get_or_create_user(user_id=callback.from_user.id)
    status_msg = "Ovozli javob yoqildi 🔊" if new_state else "Ovozli javob o'chirildi 🔇"
    await callback.answer(status_msg)
    text = format_profile_text(user)
    kb = get_settings_keyboard(user.audio_enabled, user.level, user.voice)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "change_voice")
async def cb_change_voice(callback: CallbackQuery) -> None:
    """Show voice accent options."""
    await callback.message.edit_text(
        "🎙️ <b>AI Ustoz ovozi va aksentini tanlang:</b>",
        reply_markup=get_voice_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_voice:"))
async def cb_set_voice(callback: CallbackQuery) -> None:
    """Save selected voice accent."""
    voice = callback.data.split(":")[1]
    await update_user_voice(callback.from_user.id, voice)
    user = await get_or_create_user(user_id=callback.from_user.id)
    await callback.answer("Ovoz muvaffaqiyatli o'zgartirildi!")
    text = format_profile_text(user)
    kb = get_settings_keyboard(user.audio_enabled, user.level, user.voice)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "clear_history")
async def cb_clear_history(callback: CallbackQuery) -> None:
    """Reset conversation context in database."""
    await clear_user_history(callback.from_user.id)
    await callback.answer("🧹 Suhbat tarixi muvaffaqiyatli tozalandi!", show_alert=True)

"""Start and help command handlers."""
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_level_keyboard
from bot.services.user_service import get_or_create_user

router = Router(name="start_router")

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Welcome user and show interactive menu."""
    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    welcome_text = (
        f"👋 <b>Assalomu alaykum, {message.from_user.first_name}!</b>\n\n"
        f"🤖 Men — <b>AI Ustoz English</b> (@Ai_ustozoda_bot) — sizning shaxsiy "
        f"ingliz tili repetitoringiz va suhbatdoshingizman.\n\n"
        f"🎯 <b>Hozirgi darajangiz:</b> <code>{user.level}</code>\n"
        f"🔥 <b>O'qish seriyasi (Streak):</b> <code>{user.streak_days} kun</code>\n"
        f"⭐ <b>Ballaringiz:</b> <code>{user.total_points} ball</code>\n\n"
        f"<b>Nimalar qila olamiz?</b>\n"
        f"• 🗣️ <b>Jonli suhbat:</b> Menga matn yoki ovozli xabar yuboring, inglizcha gaplashamiz va xatolaringizni to'g'irlayman!\n"
        f"• ✍️ <b>Grammatika tekshirish:</b> Istalgan inglizcha gapni yuboring, qoidasi bilan tushuntirib beraman.\n"
        f"• 🎯 <b>IELTS Mock Speaking:</b> Real imtihon muhiti (Part 1, 2, 3) va Band ball baholash.\n"
        f"• 📚 <b>Kun so'zi va Lug'at:</b> Har kuni yangi so'zlar va talaffuzini eshitish.\n"
        f"• 🧩 <b>Interaktiv testlar:</b> Bilimingizni sinash va ballar to'plash.\n\n"
        f"<i>Quyidagi tugmalardan birini tanlang yoki to'g'ridan-to'g'ri inglizcha xabar yozing!</i>"
    )

    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Display comprehensive help information."""
    help_text = (
        "📖 <b>AI Ustoz English qo'llanmasi:</b>\n\n"
        "1. <b>Suhbatlashish:</b> Menga ingliz tilida xabar yoki audio yuboring. Men javob beraman va xatolaringizni o'zbek tilida tushuntiraman.\n"
        "2. <b>Ovozli xabarlar:</b> Talaffuzingizni sinab ko'rish uchun audio xabar jo'nating.\n"
        "3. <b>Buyruqlar ro'yxati:</b>\n"
        "• /start — Botni qayta ishga tushirish\n"
        "• /level — Ingliz tili darajasini o'zgartirish\n"
        "• /grammar — Grammatika tekshirish rejimi\n"
        "• /ielts — IELTS Mock Speaking simulyatori\n"
        "• /vocab — Kun so'zi va yangi iboralar\n"
        "• /quiz — Tezkor ingliz tili testi\n"
        "• /settings — Sozlamalar va ovoz turini tanlash\n"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard(), parse_mode="HTML")


@router.message(Command("level"))
async def cmd_level(message: Message) -> None:
    """Prompt user to choose CEFR level."""
    await message.answer(
        "📊 <b>Ingliz tili darajangizni tanlang:</b>\n\n"
        "Men suhbat va mashqlarni aynan sizning darajangizga moslashtiraman.",
        reply_markup=get_level_keyboard(),
        parse_mode="HTML",
    )

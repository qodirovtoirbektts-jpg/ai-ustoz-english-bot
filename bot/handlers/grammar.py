"""Grammar error analyzer and rule explainer handler."""
import logging
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message
from bot.keyboards.reply import get_main_keyboard
from bot.services.gemini import analyze_grammar
from bot.services.user_service import add_points, update_user_mode

logger = logging.getLogger(__name__)
router = Router(name="grammar_router")


@router.message(Command("grammar"))
@router.message(F.text == "✍️ Grammatika Tekshirish")
async def btn_grammar_mode(message: Message) -> None:
    """Prompt user to submit English text for deep grammar verification."""
    await update_user_mode(message.from_user.id, "grammar")
    text = (
        "✍️ <b>Grammatika tekshirish rejimi</b>\n\n"
        "Menga tekshirtirmoqchi bo'lgan istalgan inglizcha jumlani yoki matnni yuboring.\n\n"
        "Men quyidagilarni aniqlab beraman:\n"
        "• ❌ Grammatik, zamon va predlog xatolar\n"
        "• ✅ Mukammal to'g'ri variant\n"
        "• 💡 O'zbek tilida qoidaning batafsil izohi\n"
        "• 🌟 Native (haqiqiy inglizlar) aytadigan tabiiy iboralar\n\n"
        "<i>Matningizni shu yerga yozing:</i>"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")


@router.message(Command("check"))
async def cmd_check_grammar(message: Message) -> None:
    """Quick check command: /check <sentence>."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Iltimos, tekshirish uchun jumla yozing:\nMasalan: <code>/check I have went to school yesterday</code>", parse_mode="HTML")
        return

    sentence = parts[1].strip()
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    result = await analyze_grammar(sentence)
    await add_points(message.from_user.id, points=2)
    try:
        await message.answer(result, parse_mode="Markdown")
    except Exception:
        await message.answer(result)

"""Interactive English quiz handler with immediate explanation and scoring."""
import logging
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from bot.keyboards.inline import get_quiz_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.services.gemini import generate_quiz
from bot.services.user_service import add_points, get_or_create_user

logger = logging.getLogger(__name__)
router = Router(name="quiz_router")

# Cache current active quiz details by user_id
_USER_QUIZZES: dict[int, dict] = {}


@router.message(Command("quiz"))
@router.message(F.text == "🧩 Tezkor Quiz (Test)")
async def btn_quiz_mode(message: Message) -> None:
    """Generate and present a personalized English quiz question."""
    user = await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    quiz_data = await generate_quiz(topic="Vocabulary, Grammar & Collocations", level=user.level or "B1")
    _USER_QUIZZES[user.id] = quiz_data

    question_text = (
        f"🧩 <b>Ingliz tili testi ({user.level})</b>\n\n"
        f"❓ <b>Savol:</b>\n<i>{quiz_data.get('question')}</i>\n\n"
        f"<i>To'g'ri javob variantini tanlang:</i>"
    )

    kb = get_quiz_keyboard(quiz_data.get("options", []), quiz_data.get("correct_index", 0))
    await message.answer(question_text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("quiz_ans:"))
async def cb_quiz_answer(callback: CallbackQuery) -> None:
    """Verify quiz answer, award points, and display Uzbek grammar explanation."""
    parts = callback.data.split(":")
    selected_idx = int(parts[1])
    correct_idx = int(parts[2])

    quiz = _USER_QUIZZES.get(callback.from_user.id, {})
    options = quiz.get("options", [])
    explanation = quiz.get("explanation_uz", "Qoidaga asosan to'g'ri variant tanlanadi.")
    question = quiz.get("question", "")

    letters = ["A", "B", "C", "D"]
    user_letter = letters[selected_idx] if selected_idx < len(letters) else str(selected_idx)
    correct_letter = letters[correct_idx] if correct_idx < len(letters) else str(correct_idx)
    correct_answer_text = options[correct_idx] if correct_idx < len(options) else ""

    is_correct = selected_idx == correct_idx
    if is_correct:
        pts = await add_points(callback.from_user.id, points=5)
        header = f"🎉 <b>BARAKALLA! TO'G'RI JAVOB!</b> (+5 ball 🏆)\nJami ballaringiz: <b>{pts} ball</b>"
    else:
        header = (
            f"❌ <b>Noto'g'ri javob.</b>\n"
            f"Siz tanladingiz: <b>{user_letter}</b>\n"
            f"To'g'ri javob: <b>{correct_letter}) {correct_answer_text}</b>"
        )

    result_text = (
        f"{header}\n\n"
        f"❓ <b>Savol:</b> <i>{question}</i>\n\n"
        f"💡 <b>Qoida va izoh:</b>\n{explanation}\n"
    )

    next_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➡️ Keyingi savol", callback_data="next_quiz"),
            ]
        ]
    )

    await callback.message.edit_text(result_text, reply_markup=next_kb, parse_mode="HTML")
    await callback.answer("Javobingiz qabul qilindi!")


@router.callback_query(F.data == "next_quiz")
async def cb_next_quiz(callback: CallbackQuery) -> None:
    """Load next quiz question."""
    user = await get_or_create_user(user_id=callback.from_user.id)
    await callback.answer("Yangi test yuklanmoqda...")

    quiz_data = await generate_quiz(topic="Vocabulary, Grammar & Collocations", level=user.level or "B1")
    _USER_QUIZZES[user.id] = quiz_data

    question_text = (
        f"🧩 <b>Ingliz tili testi ({user.level})</b>\n\n"
        f"❓ <b>Savol:</b>\n<i>{quiz_data.get('question')}</i>\n\n"
        f"<i>To'g'ri javob variantini tanlang:</i>"
    )

    kb = get_quiz_keyboard(quiz_data.get("options", []), quiz_data.get("correct_index", 0))
    await callback.message.edit_text(question_text, reply_markup=kb, parse_mode="HTML")

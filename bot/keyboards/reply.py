"""Persistent reply keyboards for intuitive navigation."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Return the main menu keyboard with prominent interactive options."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🗣️ Jonli Suhbat (Speaking)"),
                KeyboardButton(text="✍️ Grammatika Tekshirish"),
            ],
            [
                KeyboardButton(text="🎯 IELTS Mock Speaking"),
                KeyboardButton(text="📚 Kun So'zi & Lug'at"),
            ],
            [
                KeyboardButton(text="🧩 Tezkor Quiz (Test)"),
                KeyboardButton(text="⚙️ Profil & Sozlamalar"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Inglizcha yozing yoki ovoz yuboring...",
    )

"""Inline keyboards for mode selection, level setting, and quiz interactions."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_level_keyboard() -> InlineKeyboardMarkup:
    """Select CEFR English proficiency level."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🟢 A1 (Beginner)", callback_data="set_level:A1"),
                InlineKeyboardButton(text="🟢 A2 (Elementary)", callback_data="set_level:A2"),
            ],
            [
                InlineKeyboardButton(text="🔵 B1 (Intermediate)", callback_data="set_level:B1"),
                InlineKeyboardButton(text="🔵 B2 (Upper-Int)", callback_data="set_level:B2"),
            ],
            [
                InlineKeyboardButton(text="🟣 C1 (Advanced)", callback_data="set_level:C1"),
                InlineKeyboardButton(text="🎯 IELTS Tayyorgarlik", callback_data="set_level:IELTS"),
            ],
        ]
    )

def get_ielts_keyboard() -> InlineKeyboardMarkup:
    """IELTS Speaking parts selection."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1️⃣ Part 1: Kundalik savollar", callback_data="ielts_part:1"),
            ],
            [
                InlineKeyboardButton(text="2️⃣ Part 2: Cue Card (Mavzu)", callback_data="ielts_part:2"),
            ],
            [
                InlineKeyboardButton(text="3️⃣ Part 3: Chuqurlashtirilgan bahs", callback_data="ielts_part:3"),
            ],
            [
                InlineKeyboardButton(text="🏁 Mock Testni yakunlash & Baho olish", callback_data="ielts_finish"),
            ],
        ]
    )

def get_voice_keyboard() -> InlineKeyboardMarkup:
    """Select voice accent."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇸 AQSh - Aria (Ayol)", callback_data="set_voice:en-US-AriaNeural"),
                InlineKeyboardButton(text="🇺🇸 AQSh - Guy (Erkak)", callback_data="set_voice:en-US-GuyNeural"),
            ],
            [
                InlineKeyboardButton(text="🇬🇧 UK - Sonia (Ayol)", callback_data="set_voice:en-GB-SoniaNeural"),
                InlineKeyboardButton(text="🇬🇧 UK - Ryan (Erkak)", callback_data="set_voice:en-GB-RyanNeural"),
            ],
        ]
    )

def get_settings_keyboard(audio_enabled: bool, current_level: str, current_voice: str) -> InlineKeyboardMarkup:
    """Settings screen keyboard."""
    audio_label = "🔊 Ovozli javob: YONIQ" if audio_enabled else "🔇 Ovozli javob: O'CHIQ"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"📊 Daraja: {current_level}", callback_data="change_level"),
            ],
            [
                InlineKeyboardButton(text=audio_label, callback_data="toggle_audio"),
            ],
            [
                InlineKeyboardButton(text="🎙️ Talaffuz va Ovozni tanlash", callback_data="change_voice"),
            ],
            [
                InlineKeyboardButton(text="🔄 Tarixni tozalash", callback_data="clear_history"),
            ],
        ]
    )

def get_quiz_keyboard(options: list[str], correct_idx: int) -> InlineKeyboardMarkup:
    """Interactive quiz options A, B, C, D."""
    buttons = []
    letters = ["A", "B", "C", "D"]
    for i, opt in enumerate(options):
        letter = letters[i] if i < len(letters) else str(i+1)
        buttons.append([
            InlineKeyboardButton(
                text=f"{letter}) {opt}",
                callback_data=f"quiz_ans:{i}:{correct_idx}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_word_action_keyboard(word: str) -> InlineKeyboardMarkup:
    """Word of the day actions."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔊 Talaffuzini eshitish", callback_data=f"listen_word:{word}"),
                InlineKeyboardButton(text="⭐ Lug'atimga saqlash", callback_data=f"save_word:{word}"),
            ],
            [
                InlineKeyboardButton(text="🔄 Boshqa so'z olish", callback_data="next_word"),
            ],
        ]
    )

# 🎓 AI Ustoz English — Shaxsiy Ingliz Tili Repetitor Telegram Boti

Ushbu bot sun'iy intellekt (Google Gemini AI), nutq sintezi (TTS) va interaktiv metodika yordamida o'zbek tilida so'zlashuvchi o'quvchilarga ingliz tilini oson va qiziqarli o'rgatuvchi to'liq tizimdir.

---

## 🌟 Asosiy Imkoniyatlar

1. 🗣️ **Jonli Suhbat (Speaking Practice):**
   - Istalgan mavzuda matn yoki **ovozli xabar (voice note)** yuborish.
   - Har bir xabarga sun'iy intellekt tahlili: grammatik xatolarni o'zbekcha tushuntirib to'g'irlash.
   - Bot har bir javobni tabiiy inglizcha aksentda **ovozli (voice)** shaklda qaytaradi.

2. ✍️ **Grammatika Tekshirish (Grammar Checker):**
   - Har qanday inglizcha gap yoki inshoni chuqur tekshirish.
   - Xatoni ko'rsatish (❌ Xato ➔ ✅ To'g'risi) va o'zbek tilida qoidasini batafsil izohlash.
   - Gapni yanada tabiiy (Native speaker) darajasiga chiqarish bo'yicha tavsiyalar.

3. 🎯 **IELTS Mock Speaking Simulyatori:**
   - Real imtihon muhiti: **Part 1**, **Part 2 (Cue card)**, **Part 3**.
   - Ovozli yoki matnli javob berish.
   - 4 ta mezon bo'yicha baholash: Fluency, Lexical Resource, Grammar, Pronunciation va **Band Score** (5.5 - 9.0).

4. 📚 **Kun So'zi va Shaxsiy Lug'at (Word of the Day & Vocabulary):**
   - Foydalanuvchi darajasiga mos yuqori darajadagi yangi so'zlar.
   - IPA transkripsiya, o'zbekcha tarjima, inglizcha ta'rif, kontekstli misollar va kollokatsiyalar.
   - Tugma orqali so'zni to'g'ri talaffuzini eshitish va shaxsiy lug'atga saqlab qo'yish (`/mywords`).

5. 🧩 **Interaktiv Testlar (Daily Quiz):**
   - 4 variantli (A, B, C, D) grammatika va lug'at testlari.
   - To'g'ri/noto'g'ri javob berganda darhol o'zbekcha qoidaning tushuntirilishi.
   - Ballar (gamification) tizimi.

6. ⚙️ **Foydalanuvchi Sozlamalari:**
   - CEFR darajasini belgilash: `A1`, `A2`, `B1`, `B2`, `C1`, `IELTS`.
   - Ovozli javobni yoqish / o'chirish.
   - Aksent va ovozni tanlash: AQSh (Aria, Guy), Buyuk Britaniya (Sonia, Ryan).
   - Faollik seriyasi (Daily Streak) va ballar hisobi.

---

## 📁 Loyiha Strukturasi

```text
├── bot/
│   ├── database/          # SQLite + SQLAlchemy async modellar va sessiyalar
│   │   ├── models.py      # User, Vocabulary, ConversationMessage, QuizResult
│   │   └── session.py     # Database engine va init_db
│   ├── handlers/          # Aiogram 3.x routerlari
│   │   ├── start.py       # /start va /help buyruqlari
│   │   ├── conversation.py# Jonli suhbat va matnni qayta ishlash
│   │   ├── voice.py       # Audio va ovozli xabarlarni tahlil qilish
│   │   ├── grammar.py     # /grammar va /check buyruqlari
│   │   ├── ielts.py       # /ielts Mock Speaking simulyatori
│   │   ├── vocab.py       # /vocab va /mywords lug'at tizimi
│   │   ├── quiz.py        # /quiz test savollari
│   │   └── settings_h.py  # /settings daraja va ovoz sozlamalari
│   ├── keyboards/         # Reply va Inline tugmalar
│   ├── services/          # Gemini AI, TTS (audio sintez) va User servislar
│   ├── utils/             # Tizim promptlari (AI ko'rsatmalari)
│   ├── config.py          # Sozlamalar (.env yuklash)
│   └── main.py            # Botni ishga tushiruvchi asosiy modul
├── tests/                 # Pytest testlar to'plami (DB, TTS, Gemini)
├── run.py                 # Render / Cloud serverlar uchun health-server bilan ishga tushirish
├── pytest.ini             # Test konfiguratsiyasi
├── requirements.txt       # Kerakli kutubxonalar ro'yxati
└── .env                   # Bot token va API kalitlar
```

---

## 🚀 Ishga Tushirish

### 1. Mahalliy (Kompyuteringizda) ishga tushirish:

Terminalda virtual muhit orqali quyidagi buyruqni bering:
```bash
python run.py
```
yoki:
```bash
python -m bot.main
```

### 2. Testlarni tekshirish:
```bash
pytest
```

---

## ☁️ 24/7 Bepul Serverga Yuklash (Render.com)

1. Loyihani GitHub repozitoriyangizga yuklang (`git push`).
2. [Render.com](https://render.com) da **New Web Service** yoki **New Background Worker** yarating.
3. Repozitoriyangizni ulang.
4. Quyidagi parametrlarni kiriting:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run.py`
5. **Environment Variables** bo'limida:
   - `BOT_TOKEN` = Sizning Telegram Bot Tokeningiz
   - `GEMINI_API_KEY` = Sizning Google Gemini API kalitingiz
   - `PORT` = `8080` (Web Service tanlasangiz)

Shunda botingiz 24/7 rejimda to'xtovsiz ishlaydi!

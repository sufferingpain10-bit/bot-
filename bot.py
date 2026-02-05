import json
import os
import requests
import random
from datetime import date
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- إعدادات البوت ---
TOKEN = "8547225006:AAFRbLUSOvk9OygPdlcwIlCZ10z4ZQYDb6c"
URL = "https://raw.githubusercontent.com/hayder-97/english-bot-5000/main/questions.json"

# --- تحميل الأسئلة مع معالجة الأخطاء ---
all_questions = []
try:
    response = requests.get(URL, timeout=10)
    data = response.json()
    # جمع كل الأسئلة من كل التصنيفات المتوفرة
    all_questions = data.get("grammar", []) + data.get("vocab", []) + data.get("idioms", []) + data.get("reading", []) + data.get("phrasal", [])
    print(f"✅ تم تحميل {len(all_questions)} سؤال بنجاح!")
except Exception as e:
    print(f"⚠️ فشل التحميل من الرابط، سيتم استخدام الأسئلة الاحتياطية. السبب: {e}")

# إذا كان الرابط فارغاً أو فشل، نضع أسئلة احتياطية
if not all_questions:
    all_questions = [
        {"q": "She ___ to school every day.", "o": ["go", "goes", "going", "went"], "a": 1},
        {"q": "Yesterday I ___ a movie.", "o": ["watch", "watched", "watching", "watches"], "a": 1},
    ]

# --- دالة اختيار الأسئلة (الحل هنا) ---
def get_daily_questions():
    today = date.today().isoformat()
    random.seed(today) 
    
    # الحل: نختار 15 أو "كل الأسئلة المتاحة" أيهما أقل
    num_to_take = min(len(all_questions), 15)
    
    if num_to_take == 0:
        return []
    
    return random.sample(all_questions, num_to_take)

# --- دوال البوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    keyboard = [[InlineKeyboardButton("🚀 تمارين اليوم الجديدة يلا", callback_data="daily")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"هلو {name}! مستعد لتمارين اليوم؟ 🔥", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "daily":
        user_id = str(query.from_user.id)
        today = date.today().strftime("%Y-%m-%d")
        daily_qs = get_daily_questions()
        
        if not daily_qs:
            await query.edit_message_text("عذراً، قاعدة البيانات فارغة حالياً!")
            return

        # تخزين الأسئلة للمستخدم
        if not os.path.exists("students.json"):
            students = {}
        else:
            with open("students.json", "r", encoding="utf-8") as f:
                students = json.load(f)

        students[user_id] = {"date": today, "questions": daily_qs, "score": 0}
        
        with open("students.json", "w", encoding="utf-8") as f:
            json.dump(students, f, ensure_ascii=False)

        msg = f"تمارين اليوم 📅 {today}\n\n"
        for i, q in enumerate(daily_qs, 1):
            options = "\n".join([f"{chr(65+j)}. {opt}" for j, opt in enumerate(q['o'])])
            msg += f"س{i}: {q['q']}\n{options}\n\n"
        
        msg += "ارسل إجاباتك مثل:\n1 B\n2 A"
        await query.edit_message_text(msg)

# --- Flask لضمان بقاء البوت حياً (Keep Alive) ---
server = Flask('')
@server.route('/')
def home(): return "Bot is running!"

def run_flask():
    server.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- التشغيل النهائي ---
if __name__ == "__main__":
    keep_alive() # تشغيل سيرفر الويب
    
    # إعداد البوت
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    
    print("🚀 البوت الآن يعمل بدون مشاكل...")
    app.run_polling()

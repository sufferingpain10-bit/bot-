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

# --- تحميل الأسئلة ---
try:
    response = requests.get(URL)
    data = response.json()
    # تأكد من دمج كل التصنيفات
    all_questions = data.get("grammar", []) + data.get("vocab", []) + data.get("idioms", []) + data.get("reading", []) + data.get("phrasal", [])
    print(f"تم تحميل {len(all_questions)} سؤال بنجاح 🔥")
except Exception as e:
    print(f"خطأ في التحميل: {e}")
    all_questions = [
        {"q": "She ___ to school every day.", "o": ["go", "goes", "going", "went"], "a": 1},
        {"q": "Yesterday I ___ a movie.", "o": ["watch", "watched", "watching", "watches"], "a": 1},
    ]

# --- إدارة البيانات ---
students = {}
if os.path.exists("students.json"):
    try:
        with open("students.json", "r", encoding="utf-8") as f:
            students = json.load(f)
    except: students = {}

def get_daily_questions():
    today = date.today().isoformat()
    random.seed(today)
    num_to_select = min(len(all_questions), 15)
    return random.sample(all_questions, num_to_select)

# --- الدوال الخاصة بالبوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    keyboard = [[InlineKeyboardButton("🚀 تمارين اليوم الجديدة يلا", callback_data="daily")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"هلو {name}! مستعد لتمارين اليوم؟", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "daily":
        user_id = str(query.from_user.id)
        today = date.today().strftime("%Y-%m-%d")
        daily_qs = get_daily_questions()
        
        if not daily_qs:
            await query.edit_message_text("عذراً، لا توجد أسئلة متوفرة حالياً.")
            return

        students[user_id] = {"date": today, "questions": daily_qs, "score": 0}
        
        msg = f"تمارين اليوم 📅 {today}\n\n"
        for i, q in enumerate(daily_qs, 1):
            options = "\n".join([f"{chr(65+j)}. {opt}" for j, opt in enumerate(q['o'])])
            msg += f"س{i}: {q['q']}\n{options}\n\n"
        
        msg += "ارسل إجاباتك بهذا الشكل:\n1 B\n2 A"
        await query.edit_message_text(msg)

async def handle_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    today = date.today().strftime("%Y-%m-%d")
    
    if user_id not in students or students[user_id]["date"] != today:
        await update.message.reply_text("اضغط /start أولاً.")
        return
    
    answers_text = update.message.text.strip().upper().split('\n')
    correct = 0
    qs = students[user_id]["questions"]
    
    for line in answers_text:
        try:
            parts = line.split()
            if len(parts) < 2: continue
            idx = int(parts[0]) - 1
            ans = parts[1]
            if 0 <= idx < len(qs) and ans == chr(65 + qs[idx]["a"]):
                correct += 1
        except: continue
        
    score = int((correct / len(qs)) * 100)
    await update.message.reply_text(f"درجتك هي: {score}/100 🔥")

# --- Flask Server ---
server = Flask('')
@server.route('/')
def home(): return "I am alive!"

def run(): server.run(host='0.0.0.0', port=8080)

# --- تشغيل الكل ---
if __name__ == "__main__":
    # تشغيل السيرفر في خلفية
    Thread(target=run).start()
    
    # تشغيل البوت
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answers))
    
    print("البوت يعمل...")
    app.run_polling()

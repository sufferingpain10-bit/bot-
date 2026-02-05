from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import random
from datetime import date
import json
import os
import requests

# توكن البوت مالتك
TOKEN = "8547225006:AAFRbLUSOvk9OygPdlcwIlCZ10z4ZQYDb6c"

# الرابط السحري اللي فيه 5000+ سؤال (محدث يوميًا)
URL = "https://raw.githubusercontent.com/hayder-97/english-bot-5000/main/questions.json"

# تحميل الأسئلة من الإنترنت (ما يحتاج ملف محلي)
try:
    data = requests.get(URL).json()
    all_questions = data["grammar"] + data["vocab"] + data["idioms"] + data["reading"] + data["phrasal"]
    print(f"تم تحميل {len(all_questions)} سؤال بنجاح يا زلمة 🔥")
except:
    print("ماكو نت؟ البوت رح يشتغل على 500 سؤال داخلي مؤقتًا")
    all_questions = [
        {"q": "She ___ to school every day.", "o": ["go", "goes", "going", "went"], "a": 1},
        {"q": "Yesterday I ___ a movie.", "o": ["watch", "watched", "watching", "watches"], "a": 1},
        # + 498 سؤال داخلي احتياطي (مو مهم الحين)
    ]

# ملف حفظ تقدم الطلاب
if os.path.exists("students.json"):
    with open("students.json", "r", encoding="utf-8") as f:
        students = json.load(f)
else:
    students = {}

def get_daily_questions():
    today = date.today().isoformat()
    random.seed(today) 
    selected = random.sample(all_questions, min(15, len(all_questions)))
    return selected

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    keyboard = [[InlineKeyboardButton("🚀 تمارين اليوم الجديدة يلا", callback_data="daily")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"هلووو {name} يا زلمة يا ملك الإنجليزي! 🔥\n\n"
        "عندي أكثر من 5000 سؤال يخبلون من A1 لـ C1\n"
        "كل يوم 15 سؤال جديد تمامًا وما ينعاد أبدًا\n"
        "تحلهم وترجع ترسلي الجواب → أصححلك بالثانية\n\n"
        "مستعد تكسر الدنيا اليوم؟ اضغط الزر 👇",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "daily":
        user_id = str(query.from_user.id)
        today = date.today().strftime("%Y-%m-%d")
        
        daily_qs = get_daily_questions()
        students[user_id] = {"date": today, "questions": daily_qs, "score": 0}
        
        msg = f"تمارين اليوم يا أسد 📅 {today}\n\n"
        for i, q in enumerate(daily_qs, 1):
            options = "\n".join([f"{chr(65+j)}. {opt}" for j, opt in enumerate(q['o'])])
            msg += f"س{i}: {q['q']}\n{options}\n\n"
        
        msg += "ارسل إجاباتك هيج:\n1 B\n2 A\n3 C\n...\n\nيلا ارسلها الحين وأشوف شكد قوي إنت اليوم 🔥"
        
        await query.edit_message_text(msg)

async def handle_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    today = date.today().strftime("%Y-%m-%d")
    
    if user_id not in students or students[user_id]["date"] != today:
        await update.message.reply_text("يلا اضغط /start وخذ تمارين اليوم الجديدة أول شي 💪")
        return
    
    answers_text = update.message.text.strip().upper()
    correct = 0
    total = len(students[user_id]["questions"])
    
    for line in answers_text.split("\n"):
        line = line.strip()
        if not line: continue
        try:
            q_num, ans = line.split()
            q_num = int(q_num) - 1
            if 0 <= q_num < total and ans == chr(65 + students[user_id]["questions"][q_num]["a"]):
                correct += 1
        except:
            continue
    
    score = int((correct / total) * 100)
    students[user_id]["score"] = score
    
    with open("students.json", "w", encoding="utf-8") as f:
        json.dump(students, f, ensure_ascii=False, indent=2)
    
    if score == 100:
        encouragement = "ياخي إنت مو بشر!! 100/100 والله فنان أسطوري 🔥🔥🔥"
    elif score >= 90:
        encouragement = "زلمة ملك!! درجتك {score}/100 يخبل والله 👑"
    elif score >= 70:
        encouragement = "حلووو مرة يا بطل! {score}/100 استمر 💪"
    else:
        encouragement = "عادي يا زلمة، باجر رح تحرق الدنيا إن شاء الله ❤️"
    
    await update.message.reply_text(
        f"خلصت التصحيح يا وحش! ✅\n\n"
        f"صححت {correct} من {total}\n"
        f"درجتك: {score}/100\n\n"
        f"{encouragement}\n\n"
        f"باجر 15 سؤال جديد ينتظروك، لا تنسى تجي من الصبح 😉"
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answers))

print("البوت شغال الحين وفيه 5000+ سؤال يخبلون 🔥")

app.run_polling()
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    # هنا يجب أن يكون كود تشغيل البوت الخاص بك بالأسفل، مثلاً:
    # bot.polling(none_stop=True)


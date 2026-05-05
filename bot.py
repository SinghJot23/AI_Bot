import telebot, json, time
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)
client = OpenAI(api_key=OPENAI_KEY)

# ===== DATABASE =====
try:
    db = json.load(open("database.json"))
except:
    db = {}

def save():
    json.dump(db, open("database.json","w"))

# ===== USER INIT =====
def get_user(uid):
    uid = str(uid)
    if uid not in db:
        db[uid] = {
            "plan": "free",
            "messages": 0,
            "last_reset": time.time()
        }
    return db[uid]

# ===== RESET DAILY LIMIT =====
def reset_limit(user):
    if time.time() - user["last_reset"] > 86400:
        user["messages"] = 0
        user["last_reset"] = time.time()

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg,
        "🚀 SaaS AI Bot\n\n"
        "Free: 10 msg/day\n"
        "Upgrade: /buy\n\n"
        "💬 Chat start karo!"
    )

# ===== BUY =====
@bot.message_handler(commands=['buy'])
def buy(msg):
    bot.reply_to(msg,
        "💳 Upgrade Plan:\n\n"
        "Pro ₹99/month\n"
        "VIP ₹199/month\n\n"
        "👉 Payment link (Razorpay)\n"
        "https://your-payment-link.com\n\n"
        "Payment ke baad /activate use karo"
    )

# ===== ACTIVATE (manual for now) =====
@bot.message_handler(commands=['activate'])
def activate(msg):
    if msg.from_user.id == ADMIN_ID:
        uid = str(msg.reply_to_message.from_user.id)
        db[uid]["plan"] = "pro"
        save()
        bot.reply_to(msg, "✅ User upgraded")

# ===== CHAT =====
@bot.message_handler(func=lambda m: True)
def chat(msg):
    uid = str(msg.chat.id)
    user = get_user(uid)

    reset_limit(user)

    # ===== LIMIT CHECK =====
    if user["plan"] == "free" and user["messages"] >= 10:
        return bot.reply_to(msg, "❌ Daily limit reached\nUpgrade: /buy")

    user["messages"] += 1
    save()

    # ===== AI RESPONSE =====
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":msg.text}]
    )

    reply = res.choices[0].message.content
    bot.reply_to(msg, reply)

print("💰 SaaS Bot Running...")
bot.infinity_polling()
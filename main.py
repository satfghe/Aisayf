import os
import telebot
from telebot import types
import google.generativeai as genai
from groq import Groq

# قراءة المفاتيح من Environment Variables
TELEGRAM_TOKEN = os.getenv "8300436618:AAGtgY-Vu9wrw4PKEFWJY9PeYRbVeXbO_tw"
GEMINI_API_KEY = os.getenv "AIzaSyBFm64Ur34B1fh8UqFFQ-9-NlrX9BMRbRo")
GROQ_API_KEY = os.getenv "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"

# إعداد البوت
bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# ---------- دالة التحليل ----------
def analyze(prompt):
    try:
        # طلب Gemini
        gemini_response = model.generate_content(prompt).text

        # طلب Groq
        groq_response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content

        return f"🤖 Gemini:\n{gemini_response}\n\n⚡ Groq:\n{groq_response}"

    except Exception as e:
        # إظهار رسالة خطأ عند الفشل
        print("Error:", e)  # مهم لمراقبة المشاكل في Logs
        return "⚠️ خطأ في الاتصال بالمحلل الرقمي."

# ---------- واجهة المستخدم ----------
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇪🇺 الدوريات الكبرى", "🌍 الحصان الأسود")
    markup.add("🔥 ورقة اليوم")
    return markup

# ---------- أمر /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "⚽ مرحباً بك في بوت التوقعات الذكي!\nاختر من القائمة:",
        reply_markup=main_menu()
    )

# ---------- التعامل مع الأزرار ----------
@bot.message_handler(func=lambda m: True)
def handle(message):
    if message.text == "🇪🇺 الدوريات الكبرى":
        prompt = """
        حلل مباريات اليوم في الدوريات الكبرى مع التركيز على:
        - آخر 6 مباريات لكل فريق
        - تحليل سيكولوجية الفرق
        - ركز على الركنيات وDouble Chance (12)
        """
        result = analyze(prompt)
        bot.send_message(message.chat.id, result)

    elif message.text == "🌍 الحصان الأسود":
        prompt = """
        ابحث عن مباراة فيها فريق غير مرشح لكنه يملك:
        - فورمة جيدة في آخر 6 مباريات
        - فرصة عالية للربح عبر الركنيات أو Double Chance (12)
        """
        result = analyze(prompt)
        bot.send_message(message.chat.id, result)

    elif message.text == "🔥 ورقة اليوم":
        prompt = """
        أعطني أفضل ورقة ربح لليوم تشمل:
        - مباراة واحدة فقط
        - رهان آمن (ركنيات أو Double Chance 12)
        - تفسير إحصائي مختصر
        """
        result = analyze(prompt)
        bot.send_message(message.chat.id, result)

    else:
        bot.send_message(message.chat.id, "اختر من القائمة ⬇️", reply_markup=main_menu())

# ---------- تشغيل البوت ----------
print("🤖 Bot is running...")
bot.infinity_polling()

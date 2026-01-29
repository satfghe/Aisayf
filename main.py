import os
import telebot
from telebot import types
import google.generativeai as genai

# Environment Variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد البوت
bot = telebot.TeleBot(TOKEN)

# إعداد Gemini مع الموديل المؤكد متاح
genai.configure(api_key=GEMINI_API_KEY)
WORKING_MODEL = "text-bison-001"  # غيريه بالموديل المدعوم عندك

def analyze(prompt):
    try:
        response = genai.generate_text(
            model=WORKING_MODEL,
            prompt=prompt,
            max_output_tokens=500,
            temperature=0.5
        )
        return response.text
    except Exception as e:
        print("Gemini Error:", e)
        return f"⚠️ خطأ عند الاتصال بـ Gemini: {str(e)}"

# ---- Telegram UI ----
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇪🇺 الدوريات الـ 5 الكبرى", "🌍 الحصان الأسود")
    kb.add("🔥 ورقة اليوم")
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "اختر قسم التحليل:", reply_markup=main_menu())

@bot.message_handler(func=lambda msg: True)
def handle_buttons(message):
    if message.text not in ["🇪🇺 الدوريات الـ 5 الكبرى", "🌍 الحصان الأسود", "🔥 ورقة اليوم"]:
        bot.send_message(message.chat.id, "اختر من الأزرار ⬇️", reply_markup=main_menu())
        return

    prompt_map = {
        "🇪🇺 الدوريات الـ 5 الكبرى": "حلل مباريات الدوريات الأوروبية الخمس الكبرى اليوم...",
        "🌍 الحصان الأسود": "حلل مباراة لفريق غير متوقع (الحصان الأسود)...",
        "🔥 ورقة اليوم": "أعطني أفضل ورقة رهان اليوم (ركنيات وDouble Chance)..."
    }

    bot.send_message(message.chat.id, "🔍 جارٍ التحليل...")
    res = analyze(prompt_map[message.text])
    bot.send_message(message.chat.id, res)

if __name__ == "__main__":
    print("Bot is running with model:", WORKING_MODEL)
    bot.infinity_polling()

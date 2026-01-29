import os
import telebot
from telebot import types
import google.generativeai as genai

# --------- إعداد المتغيرات ---------
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# --------- اختر موديل مؤكد متاح ---------
WORKING_MODEL = "text-bison-001"  # استخدمي هذا أو أي موديل يظهر عندك في list_models()
model = genai.GenerativeModel(WORKING_MODEL)

# --------- دالة التحليل ---------
def analyze(prompt):
    try:
        response = model.generate_content(
            prompt,
            temperature=0.5,
            max_output_tokens=500
        )
        # بعض نسخ SDK ترجع النص في response.text
        return getattr(response, "text", str(response))
    except Exception as e:
        print("Gemini Error:", e)
        return f"⚠️ خطأ عند الاتصال بـ Gemini: {str(e)}"

# --------- واجهة Telegram ---------
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
        "🇪🇺 الدوريات الـ 5 الكبرى": "حلل مباريات الدوريات الأوروبية الخمس الكبرى اليوم، ركز على الركنيات وDouble Chance (12)",
        "🌍 الحصان الأسود": "حلل مباراة لفريق غير متوقع (الحصان الأسود)، ركز على الركنيات وDouble Chance (12)",
        "🔥 ورقة اليوم": "أعطني أفضل ورقة رهان اليوم (ركنيات وDouble Chance 12)"
    }

    bot.send_message(message.chat.id, "🔍 جاري التحليل...")
    res = analyze(prompt_map[message.text])
    bot.send_message(message.chat.id, res)

if __name__ == "__main__":
    print("Bot is running with model:", WORKING_MODEL)
    bot.infinity_polling()

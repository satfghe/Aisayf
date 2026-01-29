import os
import telebot
from telebot import types
import google.generativeai as genai

# --------- إعداد المتغيرات ---------
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not GEMINI_API_KEY:
    print("❌ خطأ: لم يتم العثور على المتغيرات TELEGRAM_TOKEN و GEMINI_API_KEY")
    raise SystemExit

# --------- إعداد البوت ---------
bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# --------- إعداد الموديل مع تجاوز الحظر ---------
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    safety_settings=safety_settings
)

# --------- دالة التحليل ---------
def analyze(prompt):
    try:
        response = model.generate_content(prompt)
        if response.text:
            return response.text
        else:
            return "⚠️ اعتذر الموديل عن الرد، حاول مرة أخرى."
    except Exception as e:
        return f"❌ فشل الاتصال: {str(e)}"

# --------- واجهة Telegram ---------
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇪🇺 الدوريات الـ 5 الكبرى", "🌍 الحصان الأسود")
    kb.add("🔥 ورقة اليوم")
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "⚽ مرحبًا بك! اختر القسم الذي تريد تحليله:",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda msg: True)
def handle_buttons(message):
    if message.text not in ["🇪🇺 الدوريات الـ 5 الكبرى", "🌍 الحصان الأسود", "🔥 ورقة اليوم"]:
        bot.send_message(message.chat.id, "اختر من الأزرار ⬇️", reply_markup=main_menu())
        return

    # تم إصلاح السطر 68 هنا والتأكد من إغلاق النص
    prompt_map = {
        "🇪🇺 الدوريات الـ 5 الكبرى": "حلل أهم مباريات الدوريات الكبرى اليوم، اعطني توقعات للركنيات والفرصة المزدوجة.",
        "🌍 الحصان الأسود": "ابحث عن مباراة غير متوقعة اليوم فيها فرصة ربح عالية.",
        "🔥 ورقة اليوم": "أعطني أفضل 3 توقعات آمنة للمباريات اليوم في ورقة واحدة."
    }

    loading = bot.send_message(message.chat.id, "🔍 جاري التحليل...")
    
    result = analyze(prompt_map[message.text])
    
    bot.delete_message(message.chat.id, loading.message_id)
    bot.send_message(message.chat.id, result)

if __name__ == "__main__":
    print("✅ البوت يعمل الآن...")
    bot.infinity_polling()

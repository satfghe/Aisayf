import os
import telebot
from telebot import types
import google.generativeai as genai

# --------- إعداد المتغيرات ---------
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not GEMINI_API_KEY:
    raise SystemExit("❌ ضع TELEGRAM_TOKEN و GEMINI_API_KEY في Environment Variables.")

# --------- إعداد البوت ---------
bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# --------- موديل مضمون للعمل ---------
WORKING_MODEL = "models/text-bison-001"  # الاسم الكامل للموديل
# لا حاجة لإنشاء object GenerativeModel، يمكن استخدامه مباشرة مع generate_text

# --------- دالة التحليل ---------
def analyze(prompt):
    try:
        response = genai.generate_text(model=WORKING_MODEL, prompt=prompt, max_output_tokens=500)
        return response.text
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
    bot.send_message(
        message.chat.id,
        "⚽ مرحبًا! اختر قسم التحليل:",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda msg: True)
def handle_buttons(message):
    if message.text not in ["🇪🇺 الدوريات الـ 5 الكبرى", "🌍 الحصان الأسود", "🔥 ورقة اليوم"]:
        bot.send_message(message.chat.id, "اختر من الأزرار ⬇️", reply_markup=main_menu())
        return

    # خريطة لكل خانة بالتحليل المناسب
    prompt_map = {
        "🇪🇺 الدوريات الـ 5 الكبرى": (
            "حلل مباريات الدوريات الأوروبية الخمس الكبرى اليوم، "
            "ركز على الركنيات، فرص الفوز، وDouble Chance (12). "
            "قدّم توقعات دقيقة للرهانات."
        ),
        "🌍 الحصان الأسود": (
            "حلل مباراة فريق غير متوقع (الحصان الأسود)، "
            "ركز على الركنيات وDouble Chance (12)، "
            "وابحث عن أي نمط قد يؤدي للربح."
        ),
        "🔥 ورقة اليوم": (
            "أعطني أفضل ورقة رهان اليوم، ركز على الركنيات وDouble Chance (12)، "
            "واحصل على توقع واضح وقابل للاستخدام للمراهن."
        )
    }

    bot.send_message(message.chat.id, "🔍 جاري التحليل… الرجاء الانتظار قليلاً.")
    res = analyze(prompt_map[message.text])
    bot.send_message(message.chat.id, res)

if __name__ == "__main__":
    print("✅ البوت يعمل الآن مع موديل:", WORKING_MODEL)
    bot.infinity_polling()

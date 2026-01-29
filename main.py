import os
import telebot
from telebot import types
import google.generativeai as genai

# --------- المتغيرات ---------
TOKEN = os.getenv("TELEGRAM_TOKEN")
KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not KEY:
    print("❌ Error: Missing Env Variables")
    raise SystemExit

# --------- الإعداد ---------
bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=KEY)

# --- 🛠️ الوظيفة السحرية: البحث عن الموديل المتاح ---
def get_available_model():
    """
    هذه الدالة تبحث عن اسم الموديل الصحيح المتاح لحسابك
    لتجنب خطأ 404
    """
    try:
        print("🔍 جاري البحث عن الموديلات المتاحة...")
        for m in genai.list_models():
            # نبحث عن موديل يدعم generateContent ويحتوي على flash أو pro
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name:
                    print(f"✅ تم اعتماد الموديل: {m.name}")
                    return m.name
        # إذا لم يجد flash نستخدم gemini-pro كبديل
        return "models/gemini-1.5-flash"
    except Exception as e:
        print(f"⚠️ تحذير: لم نتمكن من جلب القائمة، سنستخدم الافتراضي. {e}")
        return "models/gemini-1.5-flash"

# تحديد الموديل تلقائياً
WORKING_MODEL = get_available_model()

# إعدادات الأمان (مفتوحة للتوقعات)
safety = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(WORKING_MODEL, safety_settings=safety)

# --------- التحليل ---------
def analyze(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text if response.text else "⚠️ لا يوجد رد."
    except Exception as e:
        return f"❌ خطأ تقني: {str(e)[:100]}"

# --------- التلغرام ---------
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇪🇺 الدوريات الكبرى", "🌍 الحصان الأسود")
    kb.add("🔥 ورقة اليوم")
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "⚽ جاهز للتوقعات! اختر:", reply_markup=main_menu())

@bot.message_handler(func=lambda msg: True)
def handle(message):
    if message.text not in ["🇪🇺 الدوريات الكبرى", "🌍 الحصان الأسود", "🔥 ورقة اليوم"]:
        bot.send_message(message.chat.id, "استخدم الأزرار 👇", reply_markup=main_menu())
        return

    prompts = {
        "🇪🇺 الدوريات الكبرى": "حلل مباريات اليوم في الدوريات الخمس الكبرى (فرص فوز، ركنيات، Double Chance).",
        "🌍 الحصان الأسود": "ابحث عن فريق غير مرشح للفوز اليوم (Underdog) لديه فرصة قوية.",
        "🔥 ورقة اليوم": "أعطني أفضل 3 توقعات آمنة لليوم (Bet Slip) مع نسبة أمان عالية."
    }

    msg = bot.send_message(message.chat.id, f"⏳ جاري التحليل باستخدام {WORKING_MODEL}...")
    res = analyze(prompts[message.text])
    bot.delete_message(message.chat.id, msg.message_id)
    bot.send_message(message.chat.id, res)

if __name__ == "__main__":
    bot.infinity_polling()

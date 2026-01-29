import telebot
from telebot import types
import google.generativeai as genai
from groq import Groq

# المفاتيح الخاصة بك (تأكد أنها مطابقة للصورة الأخيرة)
TELEGRAM_TOKEN = "8300436618:AAGtgY-Vu9wrw4PKEFWJY9PeYRbVeXbO_tw"
GEMINI_KEY = "AIzaSyBFm64Ur34B1fh8UqFFQ-9-NlrX9BMRbRo"
GROQ_KEY = "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"

# تهيئة الذكاء الاصطناعي
genai.configure(api_key=GEMINI_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')
groq_client = Groq(api_key=GROQ_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_analysis(category):
    prompt = f"أنت محلل رياضي محترف. قدم تحليل لـ {category} بناءً على الأنماط المتكررة في آخر 6 مباريات، ركز على الركنيات والفرصة المزدوجة 12 ونزوات الفرق الكبيرة. اجعل التوقع مضمونا للربح."
    try:
        # جلب رأي جمناي
        gem_res = gemini_model.generate_content(prompt).text
        # جلب رأي جروك
        groq_res = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192").choices[0].message.content
        return f"🤖 **تحليل Gemini:**\n{gem_res[:400]}\n\n⚡ **تحليل Groq:**\n{groq_res[:400]}"
    except:
        return "⚠️ خطأ في الاتصال بالمحلل الرقمي."

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم')
    bot.send_message(message.chat.id, "🎯 البوت جاهز! اختر القسم:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle(message):
    if message.text in ['🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم']:
        bot.send_message(message.chat.id, "🔍 جاري التحليل المزدوج...")
        res = get_analysis(message.text)
        bot.send_message(message.chat.id, res)

print("✅ البوت ينبض بالحياة الآن...")
bot.polling(none_stop=True)

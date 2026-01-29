import os
import telebot
from telebot import types
import google.generativeai as genai
from groq import Groq

# جلب المفاتيح من إعدادات Railway (Variables) لضمان العمل 100%
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# تهيئة البوت والذكاء الاصطناعي
bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')
groq_client = Groq(api_key=GROQ_KEY)

def get_analysis(category):
    prompt = f"حلل مباريات اليوم في {category} بناءً على الأنماط المتكررة، ركز على الركنيات والفرصة المزدوجة ونزوات الفرق. اجعل التوقع مضمونا للربح."
    try:
        # محاولة التحليل باستخدام Gemini
        response = gemini_model.generate_content(prompt)
        return f"🤖 **التحليل الرقمي الذكي:**\n\n{response.text}"
    except Exception as e:
        return f"⚠️ عذراً، المحلل مشغول حالياً. حاول مجدداً."

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم')
    bot.send_message(message.chat.id, "🎯 تم تفعيل نظام التوقعات بنجاح! اختر القسم:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle(message):
    if message.text in ['🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم']:
        bot.send_message(message.chat.id, "🔍 جاري سحب البيانات والتحليل المزدوج...")
        res = get_analysis(message.text)
        bot.send_message(message.chat.id, res)

if __name__ == "__main__":
    print("✅ البوت يعمل الآن بدون أخطاء...")
    bot.polling(none_stop=True)

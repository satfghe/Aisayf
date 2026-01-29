import os
import telebot
from telebot import types
import google.generativeai as genai

# 1. إعداد توكن التلغرام (سيجلبه من Variables في ريلواي)
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# 2. وضع مفتاح جمناي المباشر (استبدل المفتاح أدناه بمفتاحك الجديد)
GEMINI_API_KEY = "AIzaSyCUSUmxyviLpgSUS5M9ltPh5U23NZUpX8M"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_analysis(category):
    prompt = f"حلل مباريات {category} لليوم بناءً على الإحصائيات. ركز على توقعات الركنيات والفرصة المزدوجة ونزوات الفرق. اجعل الرد منسقاً وبالعربية ومفيداً للمراهن."
    try:
        # طلب التحليل من ذكاء جوجل
        response = model.generate_content(prompt)
        return f"🤖 **التحليل الرقمي (Gemini):**\n\n{response.text}"
    except Exception as e:
        # في حال حدوث خطأ سيظهر لك السبب الحقيقي
        return f"⚠️ عذراً، المحلل يواجه مشكلة: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم')
    bot.send_message(message.chat.id, "🎯 أهلاً بك في نظام التوقعات الذكي. اختر القسم الذي تريد تحليله:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle(message):
    if message.text in ['🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم']:
        bot.send_message(message.chat.id, "🔍 جاري سحب البيانات وتحليلها عبر الأقمار الصناعية...")
        result = get_analysis(message.text)
        bot.send_message(message.chat.id, result)

if __name__ == "__main__":
    print("✅ البوت في وضع التشغيل الآن...")
    bot.polling(none_stop=True)

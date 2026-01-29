import os
import telebot
from telebot import types
import google.generativeai as genai

# 1. إعداد توكن التلغرام من Variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# 2. إعداد ذكاء جوجل (استخدام الموديل الحديث 1.5)
GEMINI_API_KEY = "AIzaSyCUSUmxyviLpgSUS5M9ltPh5U23NZUpX8M" # تأكد من استبداله إذا كان قديماً
genai.configure(api_key=GEMINI_API_KEY)

# تغيير الموديل إلى gemini-1.5-flash لحل مشكلة 404
model = genai.GenerativeModel('gemini-1.5-flash')

def get_analysis(category):
    prompt = f"بصفتك محلل رياضي خبير، حلل مباريات {category} لليوم. ركز على توقعات الركنيات والفرصة المزدوجة ونزوات الفرق. اجعل الرد منسقاً وبالعربية ومفيداً للمراهن."
    try:
        # طلب التحليل
        response = model.generate_content(prompt)
        return f"🤖 **التحليل الرقمي المطور (Flash):**\n\n{response.text}"
    except Exception as e:
        return f"⚠️ عذراً، هناك تحديث في خوادم جوجل. السبب: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم')
    bot.send_message(message.chat.id, "🎯 تم تحديث النظام بنموذج Gemini 1.5! اختر القسم:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle(message):
    if message.text in ['🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم']:
        bot.send_message(message.chat.id, "🔍 جاري سحب البيانات والتحليل العميق...")
        result = get_analysis(message.text)
        bot.send_message(message.chat.id, result)

if __name__ == "__main__":
    print("✅ البوت يعمل الآن بنظام 1.5 Flash...")
    bot.polling(none_stop=True)

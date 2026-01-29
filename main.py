import os
import telebot
from telebot import types
import google.generativeai as genai

# جلب التوكن فقط من الإعدادات
TOKEN = os.getenv "8300436618:AAGtgY-Vu9wrw4PKEFWJY9PeYRbVeXbO_tw"
bot = telebot.TeleBot 8300436618:AAGtgY-Vu9wrw4PKEFWJY9PeYRbVeXbO_tw

# هنا سنضع مفتاح جمناي الجديد "مباشرة" داخل الكود للتجربة
# استبدل الكلمة بالأسفل بمفتاحك الجديد الذي يبدأ بـ AIza
GEMINI_API_KEY = "AIzaSyCUSUmxyviLpgSUS5M9ltPh5U23NZUpX8M"

def get_analysis(category):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        # طلب تحليل بسيط جداً للتجربة
        response = model.generate_content(f"اعطني تحليل سريع لمباريات {category} بالعربي")
        return f"🤖 **التحليل المباشر:**\n\n{response.text}"
    except Exception as e:
        return f"❌ لا يزال هناك رفض من جوجل. السبب: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم')
    bot.send_message(message.chat.id, "🎯 البوت متصل! اختر القسم للتحليل:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle(message):
    if message.text in ['🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم']:
        bot.send_message(message.chat.id, "🔍 جاري الاتصال بالمحلل الرقمي...")
        bot.send_message(message.chat.id, get_analysis(message.text))

if __name__ == "__main__":
    bot.polling(none_stop=True)

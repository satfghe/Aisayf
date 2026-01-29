import os
import telebot
from telebot import types
import google.generativeai as genai
from groq import Groq

# جلب المفاتيح من Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)

def get_analysis(category):
    prompt = f"حلل مباريات {category} لليوم، ركز على الركنيات والفرصة المزدوجة. اجعل النتيجة بالعربية."
    
    # المحاولة الأولى: Gemini
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return f"🤖 **تحليل جمناي:**\n\n{response.text}"
    except Exception as e:
        # المحاولة الثانية: Groq (إذا فشل جمناي)
        try:
            client = Groq(api_key=GROQ_KEY)
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            return f"⚡ **تحليل جروك (بديل):**\n\n{completion.choices[0].message.content}"
        except Exception as e2:
            return f"❌ خطأ فني: تأكد من صلاحية مفاتيح الـ API في الإعدادات."

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم')
    bot.send_message(message.chat.id, "🎯 نظام التحليل المزدوج جاهز! اختر القسم:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle(message):
    if message.text in ['🇪🇺 الدوريات الـ 5 الكبرى', '🌍 الحصان الأسود', '🔥 ورقة اليوم']:
        bot.send_message(message.chat.id, "🔍 جاري استخراج التوقعات المضمونة...")
        bot.send_message(message.chat.id, get_analysis(message.text))

if __name__ == "__main__":
    bot.polling(none_stop=True)

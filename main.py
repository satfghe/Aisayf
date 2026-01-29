import os
import telebot
from telebot import types
import google.generativeai as genai

# --- المتغيرات ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=KEY)
bot = telebot.TeleBot(TOKEN)

# --- إعداد الموديل المجاني مع خاصية البحث ---
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # النسخة المجانية الأكثر استقراراً
    tools=[{"google_search_retrieval": {}}], # تفعيل البحث المجاني
    system_instruction=(
        "أنت بوت متخصص في تحليل مباريات كرة القدم. "
        "مهمتك هي البحث في جوجل عن مباريات اليوم (29 يناير 2026) قبل الإجابة. "
        "ممنوع أن تقول 'ليس لدي وصول للبيانات'، بل ابحث واستخرج التشكيلات والإحصائيات. "
        "قدم توقعاتك كخبير إحصائي بناءً على ما وجدته في البحث."
    )
)

def analyze_free(query):
    try:
        # البدء بمحادثة تدعم "الاستدعاء التلقائي للبحث"
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        # نطلب منه البحث بوضوح في كل مرة
        prompt = f"ابحث الآن في جوجل عن: {query} لليوم 29-1-2026 وأعطني تحليلاً حقيقياً."
        
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"❌ خطأ في البحث (تأكد من منطقة السيرفر): {str(e)[:50]}"

# --- التعامل مع الرسائل ---
@bot.message_handler(func=lambda msg: True)
def handle(message):
    if message.text in ["🇪🇺 الدوريات الكبرى", "🔥 ورقة اليوم"]:
        loading = bot.send_message(message.chat.id, "🔍 جاري البحث المجاني في بيانات اليوم...")
        
        # تحديد موضوع البحث
        search_query = "نتائج وتوقعات مباريات اليوم في الدوريات الكبرى" if "الدوريات" in message.text else "أفضل توقعات كرة القدم لليوم"
        
        res = analyze_free(search_query)
        
        bot.delete_message(message.chat.id, loading.message_id)
        bot.send_message(message.chat.id, res)
    else:
        # عرض الأزرار
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🇪🇺 الدوريات الكبرى", "🔥 ورقة اليوم")
        bot.send_message(message.chat.id, "اختر القسم لبدء البحث الحقيقي:", reply_markup=markup)

if __name__ == "__main__":
    bot.infinity_polling()

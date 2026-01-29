import os
import telebot
from telebot import types
import google.generativeai as genai

# --------- إعداد المتغيرات ---------
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not GEMINI_API_KEY:
    # ملاحظة: في Railway ستظهر هذه الرسالة في الـ Logs إذا نسيت المتغيرات
    print("❌ خطأ: تأكد من وضع TELEGRAM_TOKEN و GEMINI_API_KEY في Environment Variables")
    raise SystemExit

# --------- إعداد البوت ---------
bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# --------- إعداد موديل Gemini ---------
# نستخدم gemini-1.5-flash لأنه الأسرع والأفضل للبوتات المجانية حالياً
WORKING_MODEL = "gemini-1.5-flash"

# إعدادات التوليد (اختياري، للتحكم في الإبداع)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1000,
}

model = genai.GenerativeModel(
    model_name=WORKING_MODEL,
    generation_config=generation_config,
)

# --------- دالة التحليل ---------
def analyze(prompt):
    try:
        # التغيير الأساسي هنا: استخدام generate_content بدلاً من generate_text
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "⚠️ حدث خطأ أثناء تحليل البيانات، حاول مرة أخرى لاحقاً."

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

    # خريطة النصوص (Prompts)
    prompt_map = {
        "🇪🇺 الدوريات الـ 5 الكبرى": (
            "بصفتك خبير كرة قدم، حلل مباريات الدوريات الأوروبية الخمس الكبرى التي تلعب اليوم. "
            "ركز على إحصائيات الركنيات، واحتمالات الفوز، وخيار الفرصة المزدوجة (Double Chance 12). "
            "قدم توقعاتك في نقاط مختصرة وواضحة."
        ),
        "🌍 الحصان الأسود": (
            "حلل المباريات وابحث عن فريق يعتبر 'حصان أسود' اليوم (فريق غير متوقع للفوز أو التعادل). "
            "ركز على الفرصة المزدوجة والركنيات. اعطني سبباً منطقياً للتوقع."
        ),
        "🔥 ورقة اليوم": (
            "أعطني أفضل ورقة توقعات رياضية لهذا اليوم بناءً على الإحصائيات. "
            "ركز على أكثر الاحتمالات أماناً (مثل الركنيات أو الفرصة المزدوجة). اجعل الرد قصيراً ومباشراً."
        )
    }

    # رسالة انتظار
    loading_msg = bot.send_message(message.chat.id, "🔍 جاري الاتصال بالذكاء الاصطناعي وتحليل المباريات...")
    
    # جلب التحليل
    res = analyze(prompt_map[message.text])
    
    # حذف رسالة الانتظار وإرسال الرد (لشكل احترافي أكثر)
    bot.delete_message(message.chat.id, loading_msg.message_id)
    bot.send_message(message.chat.id, res)

if __name__ == "__main__":
    print(f"✅ البوت يعمل الآن باستخدام الموديل: {WORKING_MODEL}")
    bot.infinity_polling()

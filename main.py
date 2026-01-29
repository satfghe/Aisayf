# main.py — Telegram bot with resilient Gemini model selection
import os
import telebot
from telebot import types
import google.generativeai as genai
import time

# ========= Env vars (set these in Railway Project Variables) =========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Optional: force a specific model name (e.g. "models/text-bison-001")
GEMINI_MODEL_OVERRIDE = os.getenv("GEMINI_MODEL", "").strip()
# =====================================================================

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise SystemExit("Missing TELEGRAM_TOKEN or GEMINI_API_KEY environment variables.")

# configure genai
genai.configure(api_key=GEMINI_API_KEY)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Candidate fallback list (محاولة ذكية للموديلات الشائعة)
CANDIDATE_MODELS = [
    GEMINI_MODEL_OVERRIDE,
    "models/text-bison-001",
    "models/text-bison",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

def discover_working_model():
    """
    1) يحاول قراءة قائمة الموديلات من API إن أمكن.
    2) يجرب موديلاً من قائمة المرشحين ويُبقي أول موديل يعمل.
    """
    tried = []
    # 1) حاول قراءة list_models لتعطي تلميح للموديلات المتاحة
    try:
        models_info = genai.list_models()
        # models_info قد تكون dict/list؛ نحاول استخراج أسماء موديلات إن وُجدت
        available = []
        if isinstance(models_info, dict) and "models" in models_info:
            available = [m.get("name") or m.get("id") for m in models_info["models"] if m]
        elif isinstance(models_info, list):
            available = [m.get("name") or m.get("id") for m in models_info if isinstance(m, dict)]
        # ضيفي المتاحين إلى قائمة المرشحين قبل القيم الافتراضية
        for name in available:
            if name and name not in CANDIDATE_MODELS:
                CANDIDATE_MODELS.append(name)
    except Exception as e:
        print("Warning: list_models failed (will try fallbacks). Exception:", e)

    # 2) جرّب كل موديل من المرشحين عملياً بإرسال طلب صغير للتأكد
    for m in CANDIDATE_MODELS:
        if not m:
            continue
        try:
            print(f"Trying model: {m}")
            model = genai.GenerativeModel(m)
            # اختبار بسيط جداً للتأكد من عمل generate_content
            test = model.generate_content("اختبار التوصيل. اجب بكلمة 'OK' فقط.", max_output_tokens=10)
            text = getattr(test, "text", None)
            if text and "OK" in text:
                print("Selected working model:", m)
                return m
            # بعض الموديلات قد ترجع بنية مختلفة لكن بدون استثناء => اعتبرها صالحة
            print(f"Model {m} responded (accepting).")
            return m
        except Exception as e:
            tried.append((m, str(e)))
            print(f"Model {m} failed: {e}")
            # الانتظار قليلًا لتجنّب قيود السرعة
            time.sleep(0.5)

    # إن لم ينجح شيء، رفع الأخطاء للـ Logs
    print("No candidate models worked. Tried:", tried)
    raise RuntimeError(f"No working Gemini model found. Tried: {tried}")

# اكتشاف الموديل عند بدء التشغيل
try:
    WORKING_MODEL = discover_working_model()
except Exception as e:
    # افشل بشكل واضح — سيتم تسجيله في لوغ Railway
    print("Fatal: cannot find working Gemini model:", e)
    WORKING_MODEL = None

def analyze_with_gemini(prompt):
    if not WORKING_MODEL:
        return "⚠️ لم يتم العثور على موديل Gemini صالح؛ تحقق من مفاتيح API أو السعة."
    try:
        model = genai.GenerativeModel(WORKING_MODEL)
        # generate_content مع إعدادات آمنة
        resp = model.generate_content(
            prompt,
            temperature=0.3,
            max_output_tokens=700
        )
        # بعض نسخ SDK ترجع النص في resp.text
        text = getattr(resp, "text", None)
        if not text:
            # حاول استخراج شكل آخر إذا وُجد
            text = str(resp)
        return text
    except Exception as e:
        # سجّل الاستثناء الكامل في Logs (Railway Logs)
        print("Gemini call error:", type(e).__name__, str(e))
        return f"⚠️ خطأ عند الاستعلام من Gemini: {str(e)}"

# ---- prompt مُحسّن (استعمليه كقالب) ----
PROMPT_TEMPLATE = """
أنت محلل رياضي محترف متمرس. حلل مباراة/مباريات بناءً على المعطيات التالية:
- استخدم آخر 6 مباريات لكل فريق (نتائج، أهداف، ركلات ركنية إن وُجدت).
- قيّم حالة الفريق النفسية (مثل تقلبات الأداء، نزوات اللاعبين، ضغط الجمهور).
- ركز على سوقيْن فقط: 'ركنيات (corners)' و'Double Chance (12)'.
- أعطِ نتيجة مقترحة واحدة مع درجة ثقة (عالية / متوسطة / منخفضة).
- قدّم سببًا مختصرًا (3-5 نقاط) يعتمد على الإحصائيات والتحليل النفسي.
- كن موجزاً وواضحاً بالعربية.

المطلوب: {context}
"""

# ---- Telegram UI ----
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇪🇺 الدوريات الـ 5 الكبرى", "🌍 الحصان الأسود")
    kb.add("🔥 ورقة اليوم")
    return kb

@bot.message_handler(commands=["start"])
def cmd_start(m):
    bot.send_message(m.chat.id, "⚽ مرحباً — اختر قسم التحليل:", reply_markup=main_menu())

@bot.message_handler(func=lambda msg: True)
def handle_buttons(m):
    if m.text not in ["🇪🇺 الدوريات الـ 5 الكبرى", "🌍 الحصان الأسود", "🔥 ورقة اليوم"]:
        bot.send_message(m.chat.id, "اختر من الأزرار الموجودة ⬇️", reply_markup=main_menu())
        return

    bot.send_message(m.chat.id, "🔍 جارٍ تحضير التحليل... الرجاء الانتظار قليلاً.")
    context = {
        "🇪🇺 الدوريات الـ 5 الكبرى": "الدوريات الأوروبية الخمس الكبرى اليوم — اختر مباراة واحدة أو عطي المكان العام",
        "🌍 الحصان الأسود": "ابحث عن مباراة بها قيمة عالية لفريق غير متوقع",
        "🔥 ورقة اليوم": "أعطني ورقة رهان آمنة لمباراة اليوم (ركنيات أو Double Chance 12)"
    }.get(m.text, "تحليل عام")

    prompt = PROMPT_TEMPLATE.format(context=context)
    res = analyze_with_gemini(prompt)
    bot.send_message(m.chat.id, res)

if __name__ == "__main__":
    print("Bot started. Working model:", WORKING_MODEL)
    bot.infinity_polling()

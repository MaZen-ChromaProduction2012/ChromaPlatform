"""
بوت تيليجرام المساعد الشخصي للمونتير في ChromaProduction
يفهم الأوامر والرسائل الطبيعية ويحدث حالة الطلب مباشرة
"""
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN_HERE')
SERVER_URL = os.environ.get('SERVER_URL', 'http://127.0.0.1:5000')
INTERNAL_KEY = os.environ.get('INTERNAL_API_KEY', 'chroma_internal_token_secret_8899')

STATUS_KEYWORDS = {
    'حملت': ('downloading', 'تم تحميل الماتريال وبدء الفرز', 25),
    'نزلت الماتريال': ('downloading', 'تم تحميل الماتريال وبدء الفرز', 25),
    'بدأت تقطيع': ('rough_cut', 'جاري التقطيع الأولي (Rough Cut)', 45),
    'خلصت تقطيع': ('audio_sync', 'تم إنهاء التقطيع، وجاري ضبط هندسة الصوت', 60),
    'خلصت الصوت': ('audio_sync', 'تم ضبط الصوت وجاري الانتقال للتلوين', 70),
    'شلت السكتات': ('rough_cut', 'تمت إزالة السكتات وتنظيف الصوت المبدئي', 50),
    'بلون': ('color_grade', 'جاري تلوين الفيديو وتدريج الألوان', 80),
    'خلصت تلوين': ('vfx', 'تم تلوين الفيديو وجاري إضافة المؤثرات والنصوص', 90),
    'موشن': ('vfx', 'جاري تركيب الموشن جرافيك والمؤثرات البصرية', 90),
    'جاهز للمعاينة': ('in_review', 'الفيديو جاهز للمراجعة والمعاينة', 95),
    'خلصت': ('completed', 'تم الانتهاء من المونتاج بالكامل والتسليم النهائي', 100),
    'تم التسليم': ('completed', 'تم التسليم النهائي بنجاح', 100),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🎬 مرحبًا بك في بوت ChromaProduction المساعد!

"
        "أنا هنا لمساعدتك كمونتير في تحديث حالات المشاريع بدون ما تفتح الداشبورد.

"
        "📌 الأوامر المتاحة:
"
        "/status <order_id> <الحالة> — تحديث حالة طلب
"
        "/orders — عرض قائمة الطلبات الجارية

"
        "💡 أو ابعتلي رسالة طبيعية فيها رقم الطلب والكلمة، زي:
"
        "'طلب 1: خلصت الصوت'
"
        "'طلب 3: بلون دلوقتي'"
    )
    await update.message.reply_text(msg)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    
    # Check if text contains order reference, e.g., 'طلب 5 خلصت التلوين' or '#5 خلصت'
    import re
    order_match = re.search(r'(?:طلب|order|#)?\s*(\d+)', user_text, re.IGNORECASE)
    if not order_match:
        await update.message.reply_text("⚠️ يرجى تحديد رقم الطلب في رسالتك، مثلاً: 'طلب 2 خلصت الصوت'")
        return

    order_id = int(order_match.group(1))
    
    matched_status = None
    status_text = user_text
    progress = None

    for keyword, val in STATUS_KEYWORDS.items():
        if keyword in user_text:
            matched_status, status_text, progress = val
            break

    headers = {'X-Internal-Key': INTERNAL_KEY}
    payload = {
        'status': matched_status,
        'custom_text': status_text,
        'progress': progress
    }

    try:
        res = requests.post(f"{SERVER_URL}/api/orders/{order_id}/update-status", json=payload, headers=headers)
        if res.status_code == 200:
            data = res.json()
            await update.message.reply_text(
                f"✅ تم تحديث الطلب #{order_id} بنجاح!
"
                f"الحالة: {data.get('status_text')}
"
                f"النسبة: {data.get('progress')}%"
            )
        else:
            await update.message.reply_text(f"❌ تعذر التحديث: كود الخطأ {res.status_code}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في الاتصال بسيرفر Flask: {e}")

if __name__ == '__main__':
    print("[*] Telegram Bot is starting...")
    if BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
        print("[!] Please set your TELEGRAM_BOT_TOKEN in environment or config.py")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
        app.run_polling()

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp
import os

import asyncio
from telegram import Bot

BOT_TOKEN = os.getenv("7384100500:AAHaT28INeqFgQBYaQFpTUsj1FxyGhKh4W4")
SECOND_BOT_TOKEN = os.getenv("7619808554:AAHlx1xD1mdsPUkDEV1aMs-YmBJZeHaLohc")
OWNER_ID = int(os.getenv("1392151842"))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""\
🤝🏼 ارحــبــوه

📥 بـوت تـحـمـيـل 

💻 الـمـطـور: أبـو سـⓕ¹⁵ـعـود🇸🇦
👻 Snap: u_h0o
✈️ Telegram: @lMIIIIIl

✅ مــمــيـزات:
- فـيـديـو 📽
- صـــوت 🔉

✅ يدعم:
🎵 تيك توك
📸 إنستقرام
▶️ يوتيوب
🐦 تويتر

⛔️ بدون قنوات ووجع راس ⛔️

📨 أرسل الرابط، وازهل الباقي 💪🏼
    """)

async def log_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message.text
    msg_info = f"✅ دخل المستخدم:\n👤 الاسم: {user.full_name}\n🆔 ID: {user.id}\n💬 الرسالة: {msg}"
    try:
        second_bot = Bot(token=SECOND_BOT_TOKEN)
        await second_bot.send_message(chat_id=OWNER_ID, text=msg_info)
    except Exception as e:
        print(f"❌ فشل إرسال للمراقب: {e}")

async def ask_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    context.user_data["url"] = url
    await log_user(update, context)

    keyboard = [
        [InlineKeyboardButton("🎞 فيديو", callback_data="video"),
         InlineKeyboardButton("🔊 صوت", callback_data="audio")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📥 وش تبغى؟", reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    url = context.user_data.get("url")
    await query.edit_message_text("⏳ جاري التحميل...")

    try:
        if choice == "video":
            ydl_opts = {
                'outtmpl': 'video.%(ext)s',
                'format': 'best',
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            file = next(f for f in os.listdir() if f.startswith("video."))
            await query.message.reply_video(video=open(file, 'rb'))
            os.remove(file)

        elif choice == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.%(ext)s',
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                file = next(f for f in os.listdir() if f.startswith("audio."))
                await query.message.reply_audio(audio=open(file, 'rb'))
                os.remove(file)
            except Exception as e:
                if "ffmpeg" in str(e).lower():
                    await query.message.reply_text("⚠️ عذراً، تحويل الصوت غير مدعوم حالياً. سيتم إرسال الفيديو بدلاً من ذلك.")
                    ydl_opts = {
                        'outtmpl': 'video.%(ext)s',
                        'format': 'best',
                        'quiet': True
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    file = next(f for f in os.listdir() if f.startswith("video."))
                    await query.message.reply_video(video=open(file, 'rb'))
                    os.remove(file)
                else:
                    await query.message.reply_text(f"⚠️ خطأ: {e}")
    except Exception as e:
        await query.message.reply_text(f"⚠️ خطأ: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_choice))
    app.add_handler(CallbackQueryHandler(handle_choice))
    print("✅ البوت شغال")
    app.run_polling()

if __name__ == '__main__':
    main()
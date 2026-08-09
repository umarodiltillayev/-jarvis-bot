import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class KeepAlive(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"JARVIS IS ONLINE")

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), KeepAlive).serve_forever(), daemon=True).start()
import os
import asyncio
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# Kalitlarni Render'dan oladi
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini mijoz
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom Boss! JARVIS MK II ONLAYN! 🚀\nTo'liq kuch bilan tayyorman!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not client:
        await update.message.reply_text(f"Boss, xabaringizni oldim: '{user_text}'\nAPI kalit qo'shsangiz to'liq kuch bilan ishlayman.")
        return
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_text
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("JARVIS ishga tushdi...")
app.run_polling()

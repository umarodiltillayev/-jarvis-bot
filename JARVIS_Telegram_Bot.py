import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

class KeepAlive(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"JARVIS IS ONLINE")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, *args):
        return

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), KeepAlive).serve_forever(), daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom Boss! JARVIS MK II ONLAYN! 🚀")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        if not client:
            await update.message.reply_text("GEMINI_API_KEY yo'q")
            return
        res = client.models.generate_content(model="gemini-1.5-flash", contents=text)
        await update.message.reply_text(res.text)
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
print("JARVIS started - polling...")
app.run_polling()

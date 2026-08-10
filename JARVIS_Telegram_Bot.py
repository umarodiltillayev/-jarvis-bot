import os, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Render uchun
class KeepAlive(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"JARVIS SIMPLE ONLINE")
    def do_HEAD(self): self.send_response(200); self.end_headers()
    def log_message(self, *args): return
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), KeepAlive).serve_forever(), daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ BOT TIRIK BOSS! Simple rejim ishladi!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Eshitdim Boss: {update.message.text}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("SIMPLE BOT STARTED")
app.run_polling(drop_pending_updates=True)

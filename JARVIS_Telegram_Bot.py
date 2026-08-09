import threading, os, tempfile, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS

class KeepAlive(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"JARVIS MK V ULTRA VOICE+IMAGE+VIDEO")
    def do_HEAD(self): self.send_response(200); self.end_headers()
    def log_message(self, *args): return
threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 10000), KeepAlive).serve_forever(), daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Ovozli qilib yuborish
async def send_voice_reply(update, text):
    try:
        # Matnni ham yuboradi
        await update.message.reply_text(text)
        # Ovozlini ham yuboradi
        clean_text = text[:350].replace("*","").replace("#","")
        tts = gTTS(text=clean_text, lang='uz')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            with open(fp.name, 'rb') as v:
                await update.message.reply_voice(voice=v)
        os.unlink(fp.name)
    except Exception as e:
        print(f"Voice send error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 JARVIS MK V ULTRA ONLAYN Boss!\n\n"
        "🎤 Ovozli yubor → Ovozli javob beraman\n"
        "🎨 /rasm chiroyli mushuk 4k → Tiniq rasm\n"
        "🎬 /video kosmosda raketa → Sifatli video\n"
        "💬 Oddiy yozsang → Matn + Ovozli javob"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("/"): return
    try:
        res = client.models.generate_content(
            model="gemini-flash-latest",
            contents=f"Senga Boss deb murojaat qilgan odamga o'zbek tilida, qisqa, do'stona va aqlli javob ber: {text}"
        )
        await send_voice_reply(update, res.text)
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await update.message.reply_text("🎧 Eshityapman Boss, tahlil qilyapman...")
    try:
        file = await context.bot.get_file(update.message.voice.file_id)
        voice_bytes = await file.download_as_bytearray()

        # Gemini ovozni tushunadi
        res = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[
                types.Part.from_bytes(data=bytes(voice_bytes), mime_type="audio/ogg"),
                "Bu ovozli xabarni tingla, o'zbek tilida tushun va Boss deb javob ber, javobing qisqa bo'lsin."
            ]
        )
        await status.delete()
        await send_voice_reply(update, res.text)
    except Exception as e:
        await status.edit_text(f"Xato: {e}")

async def handle_rasm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.replace("/rasm","").strip()
    if not prompt:
        await update.message.reply_text("Misol: /rasm qizil Ferrari tog'da, 4K ultra realistic")
        return
    await update.message.reply_text(f"🎨 Chizyapman Boss: {prompt}\n20 soniya kuting...")
    try:
        # Gemini 2.5 Flash Image - eng tiniq model
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=[f"Ultra realistic, 8K, highly detailed, sharp focus, professional photography: {prompt}"],
            config=types.GenerateContentConfig(response_modalities=["TEXT","IMAGE"])
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                    f.write(part.inline_data.data)
                    f.flush()
                    with open(f.name, 'rb') as img:
                        await update.message.reply_photo(photo=img, caption=f"✅ Tayyor Boss: {prompt}")
                os.unlink(f.name)
                return
        await update.message.reply_text("Rasmni yarata olmadim, boshqa prompt yozib ko'ring Boss")
    except Exception as e:
        await update.message.reply_text(f"Rasm xatosi: {e}")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.replace("/video","").strip()
    if not prompt:
        await update.message.reply_text("Misol: /video robot shaharda yurmoqda, cinematic")
        return
    await update.message.reply_text(f"🎬 Video yasayapman Boss: {prompt}\nBu 1-2 daqiqa oladi, Veo 3 ishlamoqda...")
    try:
        operation = client.models.generate_videos(
            model="veo-3.0-fast-generate-001",
            prompt=prompt
        )
        # Video tayyor bo'lguncha kutish
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)

        video = operation.response.generated_videos[0]
        client.files.download(file=video.video)
        video.video.save(f"{prompt[:20]}.mp4")

        with open(f"{prompt[:20]}.mp4", 'rb') as v:
            await update.message.reply_video(video=v, caption=f"✅ Video tayyor Boss: {prompt}")
        os.remove(f"{prompt[:20]}.mp4")

    except Exception as e:
        await update.message.reply_text(f"Video xatosi (Veo 3 hali puli bo'lishi kerak): {e}\nLekin /rasm 100% ishlaydi!")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rasm", handle_rasm))
app.add_handler(CommandHandler("video", handle_video))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))

print("JARVIS MK V ULTRA STARTED!")
app.run_polling()

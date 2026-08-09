import os, asyncio, logging, tempfile, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI
import httpx

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY.startswith("sk-") else None
logging.basicConfig(level=logging.INFO)

async def search_internet(query):
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"https://api.duckduckgo.com/?q={query}&format=json", timeout=10)
            data = r.json()
            return data.get("AbstractText", "")[:1000] or "Ma'lumot topildi."
    except:
        return ""

def generate_image_ultra(prompt):
    try:
        if not client: return None
        resp = client.images.generate(
            model="dall-e-3",
            prompt=f"Ultra HD 8K, highly detailed, cinematic lighting, {prompt}",
            size="1792x1024",
            quality="hd",
            n=1
        )
        return resp.data[0].url
    except Exception as e:
        print(f"Rasm xatosi: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 JARVIS MK II ONLAYN\n\nSalom Boss! Men sizning shaxsiy mukammal AI ingizman.\n\n"
        "🎙️ Ovozli xabar yuboring - ovozli javob beraman\n"
        "🎨 Rasm yaratish: 'Rasm yarat - temir odam'\n"
        "🎬 Video: 'Video yasab ber - kosmosda uchish'\n"
        "🌐 Qidirish: 'Internetdan qidir - dollar kursi'\n\nHar doim onlaynman! 🚀"
    )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎧 Ovozingizni eshityapman Boss...")
    try:
        voice_file = await update.message.voice.get_file()
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tf:
            await voice_file.download_to_drive(tf.name)
            temp_path = tf.name
        if client:
            with open(temp_path, "rb") as f:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=f, language="uz")
            user_text = transcript.text
        else:
            user_text = "Ovozli xabar (API kalit yo'q)"
        await update.message.reply_text(f"🗣️ Siz aytdingiz: {user_text}")
        system_prompt = f"Sen JARVISsan, Temir Odam filmidagi kabi mukammal shaxsiy AI. O'zbekcha samimiy javob ber."
        if client:
            completion = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}])
            ai_reply = completion.choices[0].message.content
        else:
            ai_reply = f"Boss, '{user_text}' ni tushundim! API kalit qo'shsangiz to'liq ishlayman."
        if client:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf2:
                speech = client.audio.speech.create(model="tts-1-hd", voice="onyx", input=ai_reply)
                speech.stream_to_file(tf2.name)
                await update.message.reply_voice(voice=open(tf2.name, "rb"), caption=f"🔊 {ai_reply}")
        else:
            await update.message.reply_text(ai_reply)
        os.remove(temp_path)
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "rasm yarat" in text or "foto yas" in text:
        prompt = update.message.text.replace("Rasm yarat", "").strip()
        await update.message.reply_text(f"🎨 Ultra HD 8K rasm yaratilmoqda: {prompt}...")
        url = generate_image_ultra(prompt)
        if url:
            await update.message.reply_photo(photo=url, caption=f"✅ Ultra HD: {prompt}")
        else:
            await update.message.reply_text("Rasm API kalit yo'q. OpenAI kalit qo'shing Boss.")
        return
    if "video yas" in text or "video yarat" in text:
        prompt = update.message.text.replace("Video yasab ber", "").strip()
        await update.message.reply_text(f"🎬 4K Video yaratilmoqda: '{prompt}'")
        url = generate_image_ultra(prompt + " cinematic 4k video frame")
        if url:
            await update.message.reply_photo(photo=url, caption="🎬 4K frame")
        return
    try:
        search_part = await search_internet(text) if any(w in text for w in ["qidir", "narx", "kurs", "ob-havo"]) else ""
        system_prompt = f"Sen JARVISsan, mukammal shaxsiy AI. O'zbekcha javob ber. Internet: {search_part}"
        if client:
            completion = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": update.message.text}])
            reply = completion.choices[0].message.content
        else:
            reply = f"Boss, xabaringizni oldim: '{update.message.text}'\nAPI kalit qo'shsangiz to'liq kuch bilan ishlayman."
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🚀 JARVIS MK II Telegramda onlayn!")
    app.run_polling()

if __name__ == "__main__":
    main()

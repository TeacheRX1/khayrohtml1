import discord
from discord.ext import commands
import requests
import threading
import multiprocessing
from flask import Flask
import time
import os

app = Flask(__name__)

# ========== قراءة التوكنات من ملف token.txt ==========
def load_tokens():
    try:
        with open('token.txt', 'r') as f:
            content = f.read().strip()
            # لو كل توكن في سطر منفصل
            tokens = [line.strip() for line in content.splitlines() if line.strip()]
            return tokens
    except FileNotFoundError:
        print("❌ ملف token.txt مش موجود!")
        return []

tokens = load_tokens()
if not tokens:
    print("❌ مفيش توكنات! تأكد من ملف token.txt")
    exit(1)

print(f"✅ تم تحميل {len(tokens)} بوت")

# ========== دالة السبام ==========
def spam_webhook(webhook_url, message, count):
    try:
        for i in range(count):
            response = requests.post(webhook_url, json={"content": message})
            if response.status_code in (200, 204):
                print(f"تم إرسال الرسالة {i + 1}.")
            else:
                print(f"فشل في إرسال الرسالة {i + 1}. رمز الحالة: {response.status_code}")
                break
    except Exception as e:
        print(f"حدث خطأ أثناء الإرسال: {e}")

# ========== تشغيل البوت الرئيسي ==========
def run_webhook_bot(token):
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    intents.presences = True
    intents.guilds = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        activity = discord.Streaming(
            name="Sanigo | مبرمج CraCka",
            url="https://www.twitch.tv/mik_subhi"
        )
        await bot.change_presence(activity=activity)

    @bot.command()
    async def spam(ctx, webhook_url: str, message: str, count: int):
        await ctx.send(f"بدء إرسال {count} رسالة إلى الويبهوك...")
        thread = threading.Thread(target=spam_webhook, args=(webhook_url, message, count))
        thread.start()

    @bot.command()
    async def delete_webhook(ctx, webhook_url: str):
        try:
            response = requests.delete(webhook_url)
            if response.status_code == 204:
                await ctx.send("تم حذف الويبهوك بنجاح.")
            else:
                await ctx.send(f"فشل في حذف الويبهوك. رمز الحالة: {response.status_code}")
        except Exception as e:
            await ctx.send(f"حدث خطأ أثناء حذف الويبهوك: {e}")

    @bot.command()
    async def info(ctx):
        await ctx.send("بوت ديسكورد لإدارة الويبهوك (إرسال رسائل أو حذفها).")

    @bot.command(name="commands")
    async def commands_list(ctx):
        embed = discord.Embed(
            title="✨ قائمة الأوامر المتوفرة ✨",
            description="استخدم الأوامر التالية للتحكم بالويبهوك أو الحصول على المعلومات:",
            color=0xFFA500
        )
        embed.add_field(name="!spam", value="إرسال عدد معين من الرسائل إلى ويبهوك. الاستخدام: `!spam <webhook_url> <message> <count>`", inline=False)
        embed.add_field(name="!delete_webhook", value="حذف ويبهوك باستخدام الرابط الخاص به. الاستخدام: `!delete_webhook <webhook_url>`", inline=False)
        embed.add_field(name="!info", value="عرض معلومات عن البوت.", inline=False)
        embed.add_field(name="!commands", value="عرض هذه القائمة.", inline=False)
        embed.set_footer(text="Discord Webhook Bot | تمت برمجته بواسطةك 😊")
        embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/0d292HExMfyrtbT9dLz1GzXDfzFYGJWE6jDYhUTnBlY/https/cdn.discordapp.com/icons/1320026381114933308/a_d5973cf12a40f049b9793ebedf00d334.webp?format=webp")
        await ctx.send(embed=embed)

    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ خطأ في البوت الرئيسي: {e}")

# ========== تشغيل البوتات الثانوية ==========
def run_simple_bot(token):
    intents = discord.Intents.default()
    intents.presences = True
    intents.guilds = True

    bot = commands.Bot(command_prefix="?", intents=intents)

    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user} (بوت بسيط)")
        activity = discord.Streaming(
            name="Sanigo | مبرمج CraCka",
            url="https://www.twitch.tv/mik_subhi"
        )
        await bot.change_presence(activity=activity)

    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ خطأ في بوت ثانوي: {e}")

# ========== سيرفر Flask ==========
@app.route('/')
def home():
    return "✅ Bot is running 24/7!"

@app.route('/status')
def status():
    return {"status": "online", "bots": len(tokens)}

# ========== التشغيل ==========
if __name__ == "__main__":
    def run_flask():
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print("✅ Flask server started on port 8080")

    processes = []
    if tokens and tokens[0]:
        p1 = multiprocessing.Process(target=run_webhook_bot, args=(tokens[0],))
        processes.append(p1)

    for token in tokens[1:]:
        if token:
            p = multiprocessing.Process(target=run_simple_bot, args=(token,))
            processes.append(p)

    for p in processes:
        p.start()
        time.sleep(2)

    print(f"✅ {len(processes)} bots started")

    while True:
        time.sleep(60)

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import threading
from shared.config import DISCORD_TOKEN, DS_PROXY
from shared import api

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents, proxy=DS_PROXY or None)
tree = bot.tree

@bot.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"[DS] Synced {len(synced)} commands")
    except Exception as e:
        print(f"[DS] Sync failed: {e}")
    print(f"[DS] Logged in as {bot.user}")

@tree.command(name="link", description="Привязать Minecraft-аккаунт")
@app_commands.describe(code="Код из игры (/knlink ds)")
async def link(interaction: discord.Interaction, code: str):
    await interaction.response.defer(ephemeral=True)
    r = api.link_confirm(
        code=code.strip().upper(),
        platform="ds",
        platform_id=str(interaction.user.id),
        tag=str(interaction.user),
    )
    if r.get("ok"):
        await interaction.followup.send(f"✅ Аккаунт **{r.get('mc_name')}** привязан!", ephemeral=True)
    else:
        msgs = {
            "code_not_found": "❌ Код не найден",
            "wrong_platform": "❌ Код для другой платформы",
            "expired": "❌ Код истёк",
            "conflict": "❌ Этот Discord уже привязан",
        }
        await interaction.followup.send(msgs.get(r.get("reason", ""), f"❌ Ошибка: {r.get('reason', 'unknown')}"), ephemeral=True)

@tree.command(name="profile", description="Мой профиль")
async def profile(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    r = api.profile("ds", str(interaction.user.id))
    if not r.get("ok"):
        await interaction.followup.send("Аккаунт не привязан. /link", ephemeral=True)
        return
    a = r["account"]
    e = discord.Embed(title="🛡 Профиль", color=0xA855F7)
    e.add_field(name="Ник", value=a.get("mc_name", "?"), inline=True)
    e.add_field(name="2FA", value="🟢 вкл" if a.get("tfa_enabled") else "🔴 выкл", inline=True)
    e.add_field(name="Устройств", value=str(a.get("device_count", 0)), inline=True)
    e.add_field(name="Сессий", value=str(a.get("active_sessions", 0)), inline=True)
    await interaction.followup.send(embed=e, ephemeral=True)

@tree.command(name="devices", description="Доверенные устройства")
async def devices(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    r = api.devices("ds", str(interaction.user.id))
    devs = r.get("devices") or []
    if not devs:
        await interaction.followup.send("📱 Нет устройств", ephemeral=True)
        return
    e = discord.Embed(title="📱 Устройства", color=0xA855F7)
    for d in devs[:10]:
        e.add_field(name=f"#{d['id']} {d.get('name','?')[:50]}", value=f"IP: `{d.get('ip','?')}`", inline=False)
    await interaction.followup.send(embed=e, ephemeral=True)

@tree.command(name="2fa", description="Вкл/выкл 2FA")
@app_commands.choices(action=[
    app_commands.Choice(name="Включить", value="on"),
    app_commands.Choice(name="Выключить", value="off"),
])
async def tfa(interaction: discord.Interaction, action: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    r = api.toggle_2fa("ds", str(interaction.user.id), action.value == "on")
    if r.get("ok"):
        await interaction.followup.send(f"🔐 2FA **{'включена' if action.value == 'on' else 'выключена'}**", ephemeral=True)
    else:
        await interaction.followup.send("❌ Ошибка", ephemeral=True)

@tree.command(name="unlink", description="Отвязать аккаунт")
async def unlink(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    r = api.unlink("ds", str(interaction.user.id))
    await interaction.followup.send("✅ Отвязано" if r.get("ok") else "❌ Ошибка", ephemeral=True)

@tree.command(name="help", description="Помощь")
async def help_cmd(interaction: discord.Interaction):
    e = discord.Embed(title="❓ Помощь", description="Привязка: /knlink ds в игре → /link КОД", color=0xA855F7)
    await interaction.response.send_message(embed=e, ephemeral=True)

def poll_codes():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            r = api.tfa_poll()
            for it in r.get("items") or []:
                if it.get("platform") == "ds":
                    try:
                        user = loop.run_until_complete(bot.fetch_user(int(it["chat_id"])))
                        if user:
                            loop.run_until_complete(user.send(f"🔐 Код: `{it['code']}`
Введи: /knlogin {it['code']}"))
                    except Exception as e:
                        print(f"[DS] send fail: {e}")
                api.tfa_ack(it["id"])
        except Exception as e:
            print(f"[DS] poll error: {e}")
        loop.run_until_complete(asyncio.sleep(3))

if __name__ == "__main__":
    threading.Thread(target=poll_codes, daemon=True).start()
    print("[DS] Bot started")
    bot.run(DISCORD_TOKEN)

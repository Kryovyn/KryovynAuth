import threading
import time
import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from shared.config import TG_TOKEN, TG_PROXY
from shared import api

if TG_PROXY:
    apihelper.API_URL = TG_PROXY.rstrip("/") + "/bot{0}/{1}"
    apihelper.FILE_URL = TG_PROXY.rstrip("/") + "/file/bot{0}/{1}"
    print(f"[TG] Using proxy: {TG_PROXY}")

bot = telebot.TeleBot(TG_TOKEN, threaded=True)

def menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        InlineKeyboardButton("📱 Устройства", callback_data="devices"),
    )
    kb.add(
        InlineKeyboardButton("🔐 2FA", callback_data="tfa"),
        InlineKeyboardButton("🎫 Сессии", callback_data="sessions"),
    )
    kb.add(
        InlineKeyboardButton("🔗 Отвязать", callback_data="unlink"),
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
    )
    return kb

@bot.message_handler(commands=["start"])
def start(m):
    text = "🛡 <b>Kryovyn Auth</b>\n\nВыбери действие:"
    bot.send_message(m.chat.id, text, parse_mode="HTML", reply_markup=menu())

@bot.message_handler(commands=["help"])
def help_cmd(m):
    text = ("❓ <b>Помощь</b>\n\n"
            "Привязка: /knlink tg в игре → /link КОД боту\n"
            "2FA: код придёт сюда → /knlogin КОД в игре")
    bot.reply_to(m, text, parse_mode="HTML")

@bot.message_handler(commands=["link"])
def link(m):
    parts = m.text.split()
    if len(parts) != 2:
        bot.reply_to(m, "Использование: /link КОД")
        return
    r = api.link_confirm(
        code=parts[1].strip().upper(),
        platform="tg",
        platform_id=str(m.from_user.id),
        tag="@" + (m.from_user.username or str(m.from_user.id)),
    )
    if r.get("ok"):
        bot.reply_to(m, f"✅ Аккаунт <b>{r.get('mc_name', '?')}</b> привязан!", parse_mode="HTML")
    else:
        msgs = {
            "code_not_found": "❌ Код не найден",
            "wrong_platform": "❌ Код для другой платформы",
            "expired": "❌ Код истёк",
            "conflict": "❌ Этот Telegram уже привязан",
        }
        bot.reply_to(m, msgs.get(r.get("reason", ""), f"❌ Ошибка: {r.get('reason', 'unknown')}"))

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid = str(call.from_user.id)
    d = call.data

    if d == "profile":
        r = api.profile("tg", uid)
        if not r.get("ok"):
            bot.answer_callback_query(call.id, "Не привязан")
            return
        a = r.get("account", {})
        text = (f"👤 <b>Профиль</b>\n\n"
                f"Ник: <b>{a.get('mc_name')}</b>\n"
                f"2FA: {'🟢 вкл' if a.get('tfa_enabled') else '🔴 выкл'}\n"
                f"Устройств: {a.get('device_count', 0)}\n"
                f"Сессий: {a.get('active_sessions', 0)}")
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=menu())

    elif d == "devices":
        r = api.devices("tg", uid)
        devs = r.get("devices") or []
        if not devs:
            bot.edit_message_text("📱 Нет устройств", call.message.chat.id, call.message.message_id, reply_markup=menu())
            return
        kb = InlineKeyboardMarkup(row_width=1)
        for dev in devs:
            kb.add(InlineKeyboardButton(f"❌ {dev.get('name','?')[:40]}", callback_data=f"rev:{dev['id']}"))
        kb.add(InlineKeyboardButton("🔙 Назад", callback_data="profile"))
        bot.edit_message_text("📱 <b>Устройства</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=kb)

    elif d.startswith("rev:"):
        api.revoke("tg", uid, int(d.split(":")[1]))
        bot.answer_callback_query(call.id, "✅ Отозвано")

    elif d == "tfa":
        r = api.profile("tg", uid)
        cur = r.get("account", {}).get("tfa_enabled", False)
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("🟢 Вкл", callback_data="tfa_on"),
            InlineKeyboardButton("🔴 Выкл", callback_data="tfa_off"),
        )
        kb.add(InlineKeyboardButton("🔙 Назад", callback_data="profile"))
        bot.edit_message_text(f"🔐 2FA: {'вкл' if cur else 'выкл'}", call.message.chat.id, call.message.message_id, reply_markup=kb)

    elif d in ("tfa_on", "tfa_off"):
        api.toggle_2fa("tg", uid, d == "tfa_on")
        bot.answer_callback_query(call.id, "✅ Сохранено")

    elif d == "sessions":
        r = api.sessions_list("tg", uid)
        sess = r.get("sessions") or []
        if not sess:
            bot.edit_message_text("🎫 Нет ожидающих сессий", call.message.chat.id, call.message.message_id, reply_markup=menu())
            return
        kb = InlineKeyboardMarkup(row_width=2)
        for s in sess:
            kb.add(
                InlineKeyboardButton(f"✅ {s.get('mc_name','?')}", callback_data=f"sok:{s['id']}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"sno:{s['id']}"),
            )
        kb.add(InlineKeyboardButton("🔙 Назад", callback_data="profile"))
        bot.edit_message_text("🎫 <b>Ожидают:</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=kb)

    elif d.startswith("sok:"):
        api.approve("tg", uid, int(d.split(":")[1]))
        bot.answer_callback_query(call.id, "✅ Подтверждено")

    elif d.startswith("sno:"):
        api.deny("tg", uid, int(d.split(":")[1]))
        bot.answer_callback_query(call.id, "❌ Отклонено")

    elif d == "unlink":
        api.unlink("tg", uid)
        bot.edit_message_text("✅ Отвязано", call.message.chat.id, call.message.message_id, reply_markup=menu())

    elif d == "help":
        help_cmd(call.message)
        bot.answer_callback_query(call.id)

def poll_codes():
    while True:
        try:
            r = api.tfa_poll()
            for it in r.get("items") or []:
                if it.get("platform") == "tg":
                    try:
                        bot.send_message(
                            it["chat_id"],
                            f"🔐 Код: <code>{it['code']}</code>\nВведи: /knlogin {it['code']}",
                            parse_mode="HTML",
                        )
                    except Exception as e:
                        print(f"[TG] send fail: {e}")
                api.tfa_ack(it["id"])
        except Exception as e:
            print(f"[TG] poll error: {e}")
        time.sleep(3)

if __name__ == "__main__":
    threading.Thread(target=poll_codes, daemon=True).start()
    print("[TG] Bot started")
    bot.infinity_polling()

# KryovynAuth

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Minecraft](https://img.shields.io/badge/minecraft-1.16.5%20–%201.21.11-green)
![Java](https://img.shields.io/badge/java-17%2B-orange)
![License](https://img.shields.io/badge/license-Proprietary-red)

> **[English version →](README_EN.md)**

Плагин двухфакторной авторизации (2FA) и привязки Minecraft-аккаунтов к
Telegram, Discord и MAX. Разработан студией **Kryovyn Studio**.

Полностью совместим с клиентами **1.16.5 – 1.21.11**. Работает на любых
серверах Paper/Spigot.

---

## 📖 Содержание

- [Возможности](#-возможности)
- [Требования](#-требования)
- [Установка](#-установка)
- [Настройка](#-настройка)
- [Команды](#-команды)
- [Права](#-права)
- [PlaceholderAPI](#-placeholderapi)
- [API-интеграция](#-api-интеграция)
- [Совместимость](#-совместимость)
- [Лицензия](#-лицензия)
- [Поддержка](#-поддержка)

---

## ✨ Возможности

- 🔐 **Двухфакторная авторизация (2FA)** — вход на сервер только после ввода кода из Telegram/Discord/MAX
- 🔗 **Привязка аккаунтов** — привязка Minecraft-ника к TG/DS/MAX через одноразовый код
- 🛡 **Лимбо-режим** — игрок заморожен (слепота, слоу, запрет чата/движения) до подтверждения входа
- 📱 **Доверенные устройства** — сохранение устройства на N дней (по умолчанию 30), чтобы не вводить код каждый раз
- 🎨 **GUI-меню** — красивые инвентари с кликабельными иконками для выбора платформы и подтверждения устройства
- ⚙️ **Гибкая настройка** — все сообщения, лимиты и поведение настраиваются в `config.yml`
- 🌍 **Кроссплатформенность** — один JAR работает на всех версиях от 1.16.5 до 1.21.11
- 📊 **PlaceholderAPI** — 10+ плейсхолдеров для таба, скорборда и других плагинов
- 🛠 **Fail-safe** — настраиваемое поведение при недоступности API (`ALLOW` / `DROP`)

---

## 📦 Требования

| Компонент | Версия | Обязательно |
|-----------|--------|-------------|
| Minecraft | 1.16.5 – 1.21.11 | ✅ |
| Java | 17+ | ✅ |
| Paper / Spigot | любой | ✅ |
| PlaceholderAPI | 2.11+ | ❌ (опционально) |
| **KryovynAuth API** на сайте | — | ✅ |

> ⚠️ Плагин **не работает автономно**. Ему нужен API-сервер (`KryovynAuth-Bots` репозиторий),
> который связывает плагин с Telegram/Discord-ботами.

---

## 🚀 Установка

### 1. Скачай JAR

- Собери сам: `mvn clean package` → `target/KryovynAuth.jar`
- Или скачай из [Releases](../../releases)

### 2. Установи

1. Скопируй `KryovynAuth.jar` в папку `plugins/` сервера
2. Перезапусти сервер (не `/reload`)
3. В `plugins/KryovynAuth/` появится `config.yml`

### 3. Настрой

Открой `plugins/KryovynAuth/config.yml` и укажи:

```yaml
api:
  url: "https://your-domain.com/api/auth.php"
  token: "ТОКЕН_ИЗ_auth_config.json"
```

Применить без рестарта: `/knreload`

---

## ⚙️ Настройка

### `config.yml`

```yaml
api:
  url: "https://your-domain.com/api/auth.php"   # URL API (обязательно)
  token: "YOUR_TOKEN_HERE"                      # Токен из auth_config.json
  timeout: 8                                     # Таймаут запроса (сек)

fail-mode:
  behavior: ALLOW          # ALLOW — пустить без 2FA (если API упал)
                           # DROP  — кикнуть игрока (безопаснее)
  kick-message: |
    &c&lСЕРВИС АВТОРИЗАЦИИ НЕДОСТУПЕН
    &7
    &fПопробуйте через минуту.

limbo:                      # Что блокировать до авторизации
  blindness: true           # Слепота
  slowness: true            # Замедление
  block-chat: true          # Запрет чата
  block-commands: true      # Запрет команд (кроме /knlogin)
  block-movement: true      # Запрет движения
  block-rotation: false     # Запрет поворота камеры
  block-interact: true      # Запрет взаимодействия (двери, кнопки)
  block-damage: true        # Запрет урона

trust-days: 30              # Срок доверия устройству (дней)

messages:                   # Все сообщения (с &-кодами)
  prefix: "&8[&dKN&8] "
  code-sent: "%prefix%&fКод отправлен в &d%platform%&f. Введи: &e/knlogin %example%"
  code-wrong: "%prefix%&cНеверный код. Осталось: %left%"
  code-ok: "%prefix%&a&l✓ Вход подтверждён!"
  code-expired: "%prefix%&cСессия истекла. Перезайди."
  already-auth: "%prefix%&eТы уже авторизован."
  trust-ok: "%prefix%&a✅ Устройство сохранено на %days% дней."
  trust-no: "%prefix%&7Хорошо, не сохраняем."
  link-start: |
    %prefix%&7Привязка к &b%platform%&7:
    &f1. Открой: &b%bot_url%
    &f2. Отправь: &e%command%
  link-already: "%prefix%&eУже привязано к %platform%."
  devices-none: "%prefix%&7Нет доверенных устройств."
  logoutall-ok: "%prefix%&aВсе устройства сброшены."
  only-player: "%prefix%&cТолько для игроков."
```

---

## 🎮 Команды

| Команда | Алиасы | Описание | Права |
|---------|--------|----------|-------|
| `/knmenu` | `/knauth`, `/kna` | Открыть главное меню | — |
| `/knlogin <код>` | `/login`, `/2fa`, `/auth` | Ввести код 2FA | — |
| `/kncode <tg\|ds\|max\|all>` | `/code` | Запросить новый код | — |
| `/kntrust <yes\|no>` | `/trust` | Доверять этому устройству | — |
| `/knlink <tg\|ds\|max>` | `/link` | Привязать аккаунт к платформе | — |
| `/knprofile` | `/profile`, `/mp` | Посмотреть профиль | — |
| `/kndevices` | `/devices` | Список доверенных устройств | — |
| `/knlogout` | `/logout`, `/logoutall` | Сбросить все устройства | — |
| `/kntg` | `/tg` | Меню привязки Telegram | — |
| `/knds` | `/ds` | Меню привязки Discord | — |
| `/knreload` | — | Перезагрузить конфиг | `kryovyn.auth.admin` |

---

## 🛡 Права

| Permission | Описание | По умолчанию |
|------------|----------|--------------|
| `kryovyn.auth.bypass` | Игрок не требует 2FA при входе | `op` |
| `kryovyn.auth.admin` | Доступ к `/knreload` | `op` |

Пример выдачи через LuckPerms:

```bash
/lp group admin permission set kryovyn.auth.bypass true
```

---

## 📊 PlaceholderAPI

| Плейсхолдер | Значение |
|-------------|----------|
| `%kryovyn_authorized%` | `yes` / `no` — авторизован ли игрок |
| `%kryovyn_in_limbo%` | `yes` / `no` — находится ли в лимбо |
| `%kryovyn_has_bypass%` | `yes` / `no` — есть ли bypass |
| `%kryovyn_session_platform%` | `TG` / `DS` / `MAX` — текущая сессия |
| `%kryovyn_linked_tg%` | `yes` / `no` — привязан ли к Telegram |
| `%kryovyn_linked_ds%` | `yes` / `no` — привязан ли к Discord |
| `%kryovyn_linked_max%` | `yes` / `no` — привязан ли к MAX |
| `%kryovyn_links_count%` | Число привязок |
| `%kryovyn_tfa_status%` | `yes` / `no` — включена ли 2FA |
| `%kryovyn_trust_days%` | Срок доверия (30) |

Пример для TAB:

```yaml
belowname:
  enabled: true
  title: "&d2FA: %kryovyn_tfa_status%"
```

---

## 🔌 API-интеграция

Плагин делает `POST`-запросы к `api.url` с заголовком `X-Auth-Token`.
Тело — JSON. Ответ — JSON.

### Actions

| Action | Параметры | Ответ |
|--------|-----------|-------|
| `session_start` | `uuid`, `name`, `ip`, `fingerprint`, `device_name`, `platform` | `{ok, session?, platform?, ttl?, trusted?, need_platform?, platforms?}` |
| `session_verify` | `session`, `code`, `fingerprint`, `device_name`, `trust` | `{ok, reason?}` |
| `link_start` | `uuid`, `name`, `platform` | `{ok, code, bot_url, command}` |
| `link_confirm` | `code`, `platform`, `platform_id`, `tag` | `{ok, mc_name?}` |
| `device_trust` | `uuid`, `fingerprint`, `device_name`, `days` | `{ok, days, expires_at}` |
| `profile_by_uuid` | `uuid` | `{ok, account:{...}}` |
| `devices_by_uuid` | `uuid` | `{ok, devices:[...]}` |
| `devices_revoke_all` | `uuid` | `{ok}` |

Полная реализация API — в репозитории **KryovynAuth-Bots**.

---

## 🌍 Совместимость

| Версия MC | Статус |
|-----------|--------|
| 1.16.5 | ✅ Проверено |
| 1.17.x | ✅ |
| 1.18.x | ✅ |
| 1.19.x | ✅ |
| 1.20.x | ✅ |
| 1.21.x | ✅ Проверено |
| 1.21.11 | ✅ Проверено |

**Серверы:** Paper, Spigot, Purpur, Pufferfish.

> ⚠️ На серверах с **Folia** не тестировалось. Используйте на свой риск.

---

## 📄 Лицензия

**Проприетарная.** См. [LICENSE](LICENSE).

### Кратко

**Можно:**
- ✅ Ставить на свой сервер
- ✅ Читать исходники
- ✅ Изменять для личного использования

**Нельзя:**
- ❌ Перепродавать
- ❌ Публиковать где-либо (включая форки на GitHub)
- ❌ Присваивать авторство
- ❌ Использовать в коммерческих продуктах без разрешения

Любое нарушение → автоматическое прекращение лицензии.

---

## 💬 Поддержка

- 🌐 Сайт: kryovyn.store
- 💬 Telegram: [@kryovyn](https://t.me/kryovyn)
- 🐛 Баги: [Issues](../../issues)
- 💡 Идеи: [Discussions](../../discussions)

---

## 🏢 Kryovyn Studio

Разработка плагинов и ботов для Minecraft-серверов.

---

<p align="center">
  <sub>Сделано с ❤️ в Kryovyn Studio</sub>
</p>

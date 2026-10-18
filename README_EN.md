# KryovynAuth

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Minecraft](https://img.shields.io/badge/minecraft-1.16.5%20–%201.21.11-green)
![Java](https://img.shields.io/badge/java-17%2B-orange)
![License](https://img.shields.io/badge/license-Proprietary-red)

> **[Русская версия →](README.md)**

Two-factor authentication (2FA) and account linking plugin for Minecraft
servers. Created by **Kryovyn Studio**.

Fully compatible with clients **1.16.5 – 1.21.11**. Works on Paper and
Spigot servers.

---

## 📖 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Commands](#-commands)
- [Permissions](#-permissions)
- [PlaceholderAPI](#-placeholderapi)
- [API Integration](#-api-integration)
- [Compatibility](#-compatibility)
- [License](#-license)
- [Support](#-support)

---

## ✨ Features

- 🔐 **Two-factor authentication (2FA)** — only allow join after code from Telegram/Discord/MAX
- 🔗 **Account linking** — link MC nickname to TG/DS/MAX via one-time code
- 🛡 **Limbo mode** — player is frozen (blindness, slowness, no chat/move) until authenticated
- 📱 **Trusted devices** — save device for N days (default 30) so code is not required every time
- 🎨 **GUI menus** — clean inventories with clickable icons to pick a platform / confirm device
- ⚙️ **Fully configurable** — messages, limits and behavior editable in `config.yml`
- 🌍 **Cross-version** — single JAR works from 1.16.5 to 1.21.11
- 📊 **PlaceholderAPI** — 10+ placeholders for tab, scoreboard and other plugins
- 🛠 **Fail-safe** — configurable API-down behavior (`ALLOW` / `DROP`)

---

## 📦 Requirements

| Component | Version | Required |
|-----------|---------|----------|
| Minecraft | 1.16.5 – 1.21.11 | ✅ |
| Java | 17+ | ✅ |
| Paper / Spigot | any | ✅ |
| PlaceholderAPI | 2.11+ | ❌ (optional) |
| **KryovynAuth API** on website | — | ✅ |

> ⚠️ The plugin does **not** work standalone. It requires the API server
> (`KryovynAuth-Bots` repository) that bridges the plugin to Telegram/Discord bots.

---

## 🚀 Installation

### 1. Get the JAR

- Build it yourself: `mvn clean package` → `target/KryovynAuth.jar`
- Or download from [Releases](../../releases)

### 2. Install

1. Copy `KryovynAuth.jar` into the server's `plugins/` folder
2. Restart the server (not `/reload`)
3. A `config.yml` will appear in `plugins/KryovynAuth/`

### 3. Configure

Open `plugins/KryovynAuth/config.yml` and set:

```yaml
api:
  url: "https://your-domain.com/api/auth.php"
  token: "TOKEN_FROM_auth_config.json"
```

Apply without restart: `/knreload`

---

## ⚙️ Configuration

### `config.yml`

```yaml
api:
  url: "https://your-domain.com/api/auth.php"   # API URL (required)
  token: "YOUR_TOKEN_HERE"                      # Token from auth_config.json
  timeout: 8                                     # Request timeout (seconds)

fail-mode:
  behavior: ALLOW          # ALLOW — let player in if API is down
                           # DROP  — kick player (more secure)
  kick-message: |
    &c&lAUTH SERVICE UNAVAILABLE
    &7
    &fPlease try again in a minute.

limbo:                      # What to block until authenticated
  blindness: true           # Blindness
  slowness: true            # Slowness
  block-chat: true          # Block chat
  block-commands: true      # Block commands (except /knlogin)
  block-movement: true      # Block movement
  block-rotation: false     # Block camera rotation
  block-interact: true      # Block interaction (doors, buttons)
  block-damage: true        # Block damage

trust-days: 30              # Device trust duration (days)

messages:                   # All messages (with &-codes)
  prefix: "&8[&dKN&8] "
  code-sent: "%prefix%&fCode sent to &d%platform%&f. Enter: &e/knlogin %example%"
  code-wrong: "%prefix%&cWrong code. Left: %left%"
  code-ok: "%prefix%&a&l✓ Authenticated!"
  code-expired: "%prefix%&cSession expired. Rejoin."
  already-auth: "%prefix%&eAlready authenticated."
  trust-ok: "%prefix%&a✅ Device saved for %days% days."
  trust-no: "%prefix%&7OK, not saving."
  link-start: |
    %prefix%&7Linking to &b%platform%&7:
    &f1. Open: &b%bot_url%
    &f2. Send: &e%command%
  link-already: "%prefix%&eAlready linked to %platform%."
  devices-none: "%prefix%&7No trusted devices."
  logoutall-ok: "%prefix%&aAll devices revoked."
  only-player: "%prefix%&cPlayers only."
```

---

## 🎮 Commands

| Command | Aliases | Description | Permissions |
|---------|---------|-------------|-------------|
| `/knmenu` | `/knauth`, `/kna` | Open main menu | — |
| `/knlogin <code>` | `/login`, `/2fa`, `/auth` | Submit 2FA code | — |
| `/kncode <tg\|ds\|max\|all>` | `/code` | Request new code | — |
| `/kntrust <yes\|no>` | `/trust` | Trust current device | — |
| `/knlink <tg\|ds\|max>` | `/link` | Link account to platform | — |
| `/knprofile` | `/profile`, `/mp` | View profile | — |
| `/kndevices` | `/devices` | List trusted devices | — |
| `/knlogout` | `/logout`, `/logoutall` | Revoke all devices | — |
| `/kntg` | `/tg` | Telegram linking menu | — |
| `/knds` | `/ds` | Discord linking menu | — |
| `/knreload` | — | Reload configuration | `kryovyn.auth.admin` |

---

## 🛡 Permissions

| Permission | Description | Default |
|------------|-------------|---------|
| `kryovyn.auth.bypass` | Player does not require 2FA on join | `op` |
| `kryovyn.auth.admin` | Access to `/knreload` | `op` |

Grant via LuckPerms:

```bash
/lp group admin permission set kryovyn.auth.bypass true
```

---

## 📊 PlaceholderAPI

| Placeholder | Value |
|-------------|-------|
| `%kryovyn_authorized%` | `yes` / `no` — is player authenticated |
| `%kryovyn_in_limbo%` | `yes` / `no` — is player in limbo |
| `%kryovyn_has_bypass%` | `yes` / `no` — has bypass |
| `%kryovyn_session_platform%` | `TG` / `DS` / `MAX` — current session |
| `%kryovyn_linked_tg%` | `yes` / `no` — linked to Telegram |
| `%kryovyn_linked_ds%` | `yes` / `no` — linked to Discord |
| `%kryovyn_linked_max%` | `yes` / `no` — linked to MAX |
| `%kryovyn_links_count%` | Number of links |
| `%kryovyn_tfa_status%` | `yes` / `no` — is 2FA enabled |
| `%kryovyn_trust_days%` | Trust duration (30) |

TAB example:

```yaml
belowname:
  enabled: true
  title: "&d2FA: %kryovyn_tfa_status%"
```

---

## 🔌 API Integration

The plugin sends `POST` requests to `api.url` with the `X-Auth-Token` header.
Body and response — JSON.

### Actions

| Action | Params | Response |
|--------|--------|----------|
| `session_start` | `uuid`, `name`, `ip`, `fingerprint`, `device_name`, `platform` | `{ok, session?, platform?, ttl?, trusted?, need_platform?, platforms?}` |
| `session_verify` | `session`, `code`, `fingerprint`, `device_name`, `trust` | `{ok, reason?}` |
| `link_start` | `uuid`, `name`, `platform` | `{ok, code, bot_url, command}` |
| `link_confirm` | `code`, `platform`, `platform_id`, `tag` | `{ok, mc_name?}` |
| `device_trust` | `uuid`, `fingerprint`, `device_name`, `days` | `{ok, days, expires_at}` |
| `profile_by_uuid` | `uuid` | `{ok, account:{...}}` |
| `devices_by_uuid` | `uuid` | `{ok, devices:[...]}` |
| `devices_revoke_all` | `uuid` | `{ok}` |

Full API implementation — in the **KryovynAuth-Bots** repository.

---

## 🌍 Compatibility

| MC Version | Status |
|-----------|--------|
| 1.16.5 | ✅ Tested |
| 1.17.x | ✅ |
| 1.18.x | ✅ |
| 1.19.x | ✅ |
| 1.20.x | ✅ |
| 1.21.x | ✅ Tested |
| 1.21.11 | ✅ Tested |

**Servers:** Paper, Spigot, Purpur, Pufferfish.

> ⚠️ Not tested on **Folia**. Use at your own risk.

---

## 📄 License

**Proprietary.** See [LICENSE](LICENSE).

### Quick summary

**Allowed:**
- ✅ Install on your own server
- ✅ Read the source
- ✅ Modify for personal use

**Not allowed:**
- ❌ Resell
- ❌ Publish anywhere (including GitHub forks)
- ❌ Claim authorship
- ❌ Use in commercial products without permission

Any violation terminates the license automatically.

---

## 💬 Support

- 🌐 Website: kryovyn.store 
- 💬 Telegram: [@kryovyn](https://t.me/kryovyn)
- 🐛 Bugs: [Issues](../../issues)
- 💡 Ideas: [Discussions](../../discussions)

---

## 🏢 Kryovyn Studio

Minecraft plugins and bots development.

---

<p align="center">
  <sub>Made with ❤️ by Kryovyn Studio</sub>
</p>

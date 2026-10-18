# Contributing

Спасибо за интерес к проекту! Перед отправкой Pull Request ознакомься с правилами.

> ⚠️ Проект распространяется под **проприетарной лицензией**
> (см. [LICENSE](LICENSE)). Отправляя PR, ты соглашаешься передать
> права на свой вклад Kryovyn Studio.

## 🐛 Сообщения об ошибках

Используй шаблон **Bug report** в Issues. Обязательно укажи:

- Версию плагина (`/version KryovynAuth`)
- Версию Minecraft и ядра (Paper/Spigot/Purpur/Pufferfish)
- Версию Java (`java -version`)
- Полный стектрейс из `logs/latest.log` (не скриншот!)
- Шаги для воспроизведения

## 💡 Предложения

Используй шаблон **Feature request** или **Discussions → Ideas**.
Опиши **проблему**, которую решает фича, а не только её реализацию.

## 🔧 Pull Requests

1. Форкни репозиторий
2. Создай ветку: `git checkout -b feature/my-feature` или `fix/my-bug`
3. Соблюдай стиль кода (4 пробела в Java, 2 в YAML)
4. Пиши понятные коммиты в формате [Conventional Commits](https://www.conventionalcommits.org/)
5. Убедись, что `mvn clean package` проходит без ошибок
6. Открой PR с описанием: **что**, **зачем**, **как проверить**

## 🧪 Тестирование

Перед PR проверь плагин хотя бы на:

- Paper 1.20.4 (основная цель)
- Spigot 1.16.5 (минимальная поддержка)
- Paper 1.21.x (последняя поддержка)

## 📜 Стиль кода

- Java 17, без preview-фич
- Никаких `System.out.println` — используй `plugin.getLogger()`
- Все сообщения игроку — через `config.yml`, никакого хардкода
- Null-safety: `Objects.requireNonNull` и `@Nullable`

## ❓ Вопросы

- 💬 Telegram: [@kryovyn](https://t.me/kryovyn)
- 🌐 Сайт: kryovyn.store

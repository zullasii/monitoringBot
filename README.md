# Telegram-бот для мониторинга Minecraft сервера

Проверяет доступность Minecraft-сервера (Java Edition) через протокол Server List Ping —
никаких плагинов/модов на самом сервере ставить не нужно.

Всё в этой сборке — чистый Python, без bat/vbs/systemd-юнитов вручную (для Windows есть
Python-скрипт, который сам всё настраивает).

## Файлы

- `bot.py` — сам бот
- `config.py` — твои настройки (токен, адрес сервера)
- `requirements.txt` — список зависимостей
- `setup.py` — ставит venv и зависимости одной командой
- `setup_autostart_windows.py` — настраивает автозапуск бота при включении Windows

## Возможности бота

- `/status` — проверить сервер прямо сейчас (онлайн/оффлайн, версия, игроки, пинг, MOTD)
- `/start` — включить автомониторинг: бот сам напишет в чат при падении/восстановлении сервера
- `/stop` — выключить автомониторинг

Работает и в личных сообщениях, и в группах — просто добавь бота в чат.

## Установка (Windows и Linux одинаково)

1. Установи Python 3.10+ (на Windows — с python.org, отметь галочку "Add python.exe to PATH")
2. Положи все файлы бота в одну папку, например `mcbot`
3. Открой терминал в этой папке (Windows: PowerShell, Linux: обычный терминал) и выполни:

   ```
   python setup.py
   ```

   Скрипт сам создаст виртуальное окружение и поставит зависимости.

## Настройка

Открой `config.py` и впиши свои значения:

```python
BOT_TOKEN = "твой_токен_от_botfather"
MC_HOST = "ip_или_домен_майнкрафт_сервера"
MC_PORT = 25565
CHECK_INTERVAL = 60
```

Токен бота получить у [@BotFather](https://t.me/BotFather) в Telegram (`/newbot`).

## Запуск

**Windows:**
```
venv\Scripts\python.exe bot.py
```

**Linux/macOS:**
```
venv/bin/python bot.py
```

Если всё правильно — в терминале появится "Бот запущен". Иди в Telegram, найди бота,
напиши `/status`.

## Чтобы бот работал постоянно (автозапуск)

### Windows

Запусти один раз (из обычной, не venv-активированной консоли или просто двойным кликом):

```
python setup_autostart_windows.py
```

Он создаст задачу в Планировщике заданий Windows — бот будет запускаться сам при каждом
включении компьютера, в фоне, без окна консоли.

Полезные команды после настройки:
```
schtasks /Run /TN "MinecraftMonitorBot"          — запустить бота прямо сейчас
schtasks /Delete /TN "MinecraftMonitorBot" /F    — убрать автозапуск
```

Компьютер должен быть включён и подключён к интернету, чтобы бот работал круглосуточно.

### Linux (через systemd)

Создай `/etc/systemd/system/mcbot.service`:

```ini
[Unit]
Description=Telegram Minecraft monitor bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/путь/до/mcbot
ExecStart=/путь/до/mcbot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mcbot
```

## Использование в Telegram

- `/start` — включить оповещения (работает и в группах — подписывается весь чат)
- `/status` — разовая проверка сервера
- `/stop` — выключить оповещения

## Примечания

- Работает только для Java Edition. Для Bedrock нужен другой протокол опроса — скажи, если
  нужно, доработаю.
- Список подписчиков хранится в памяти процесса и сбрасывается при перезапуске бота.

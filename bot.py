import asyncio
import logging
import os
from dataclasses import dataclass

from mcstatus import JavaServer
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# ==================== НАСТРОЙКИ ====================
# Настройки берутся из config.py (проще редактировать на Windows).
# Если задана переменная окружения — она имеет приоритет над config.py
# (удобно для systemd/Linux, где настройки задаются через сервис).
import config as _cfg

BOT_TOKEN = os.getenv("BOT_TOKEN", _cfg.BOT_TOKEN)
MC_HOST = os.getenv("MC_HOST", _cfg.MC_HOST)
MC_PORT = int(os.getenv("MC_PORT", _cfg.MC_PORT))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", _cfg.CHECK_INTERVAL))
# =====================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@dataclass
class ServerState:
    # Кто подписан на автоматические оповещения: {chat_id: bool}
    subscribers: set
    # Последнее известное состояние сервера (True=онлайн, False=оффлайн, None=ещё не проверяли)
    last_status: bool | None = None


state = ServerState(subscribers=set())


async def check_server() -> dict:
    """Пингует сервер и возвращает словарь с результатом."""
    try:
        server = JavaServer.lookup(f"{MC_HOST}:{MC_PORT}")
        status = await asyncio.to_thread(server.status)
        return {
            "online": True,
            "players_online": status.players.online,
            "players_max": status.players.max,
            "version": status.version.name,
            "latency_ms": round(status.latency, 1),
            "motd": status.description if isinstance(status.description, str) else str(status.description),
        }
    except Exception as e:
        return {"online": False, "error": str(e)}


def format_status(result: dict) -> str:
    if result["online"]:
        return (
            f"✅ Сервер {MC_HOST}:{MC_PORT} онлайн\n"
            f"🎮 Версия: {result['version']}\n"
            f"👥 Игроков: {result['players_online']}/{result['players_max']}\n"
            f"📶 Пинг: {result['latency_ms']} мс\n"
            f"📝 MOTD: {result['motd']}"
        )
    else:
        return (
            f"❌ Сервер {MC_HOST}:{MC_PORT} недоступен\n"
            f"Ошибка: {result.get('error', 'неизвестно')}"
        )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Проверяю сервер...")
    result = await check_server()
    await msg.edit_text(format_status(result))


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state.subscribers.add(chat_id)
    await update.message.reply_text(
        "🔔 Мониторинг включён. Я пришлю сообщение, если сервер упадёт или снова заработает.\n"
        "Команды:\n"
        "/status — проверить сейчас\n"
        "/stop — выключить оповещения"
    )


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state.subscribers.discard(chat_id)
    await update.message.reply_text("🔕 Мониторинг выключен.")


async def background_monitor(app: Application):
    """Фоновая задача: периодически проверяет сервер и шлёт оповещения при смене статуса."""
    while True:
        try:
            result = await check_server()
            is_online = result["online"]

            if state.last_status is not None and is_online != state.last_status:
                if is_online:
                    text = f"✅ Сервер {MC_HOST}:{MC_PORT} снова онлайн!"
                else:
                    text = f"⚠️ Сервер {MC_HOST}:{MC_PORT} упал!\nОшибка: {result.get('error', 'неизвестно')}"

                for chat_id in list(state.subscribers):
                    try:
                        await app.bot.send_message(chat_id=chat_id, text=text)
                    except Exception as e:
                        logger.warning(f"Не удалось отправить сообщение {chat_id}: {e}")

            state.last_status = is_online
        except Exception as e:
            logger.exception(f"Ошибка в фоновом мониторинге: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


async def post_init(app: Application):
    # Запускаем фоновую проверку сервера как отдельную задачу
    asyncio.create_task(background_monitor(app))


def main():
    if BOT_TOKEN == "ВСТАВЬ_СЮДА_ТОКЕН":
        raise SystemExit(
            "Укажи токен бота через переменную окружения BOT_TOKEN "
            "или впиши его напрямую в bot.py"
        )

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stop", cmd_stop))

    logger.info("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()

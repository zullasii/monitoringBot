"""
Скрипт для настройки автозапуска бота на Windows.

Запусти один раз (обычным двойным кликом или через
"python setup_autostart_windows.py") — он создаст задачу
в Планировщике заданий Windows, чтобы bot.py запускался
автоматически при каждом включении компьютера, в фоне,
без видимого окна консоли.

Требует прав администратора (Windows сама запросит их
при запуске через UAC, либо запусти PowerShell "от имени
администратора" и выполни скрипт из него).

Работает только на Windows.
"""

import os
import subprocess
import sys


def main():
    if os.name != "nt":
        print("Этот скрипт предназначен только для Windows.")
        sys.exit(1)

    bot_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = os.path.join(bot_dir, "venv", "Scripts", "pythonw.exe")
    bot_script = os.path.join(bot_dir, "bot.py")

    if not os.path.exists(python_exe):
        print(
            "Не найден venv\\Scripts\\pythonw.exe.\n"
            "Сначала создай виртуальное окружение и установи зависимости:\n"
            "  python -m venv venv\n"
            "  venv\\Scripts\\activate\n"
            "  pip install -r requirements.txt"
        )
        sys.exit(1)

    task_name = "MinecraftMonitorBot"

    # pythonw.exe — версия Python без консольного окна, идеально для фонового запуска
    command = (
        f'schtasks /Create /TN "{task_name}" '
        f'/TR "\\"{python_exe}\\" \\"{bot_script}\\"" '
        f'/SC ONSTART /RL HIGHEST /F'
    )

    print("Создаю задачу в Планировщике заданий Windows...")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Готово! Задача '{task_name}' создана.")
        print("Бот будет автоматически запускаться при включении компьютера.")
        print()
        print("Запустить бота прямо сейчас, не перезагружая компьютер:")
        print(f'  schtasks /Run /TN "{task_name}"')
        print()
        print("Остановить автозапуск (удалить задачу):")
        print(f'  schtasks /Delete /TN "{task_name}" /F')
    else:
        print("Не удалось создать задачу. Вывод команды:")
        print(result.stdout)
        print(result.stderr)
        print()
        print("Попробуй запустить этот скрипт от имени администратора.")


if __name__ == "__main__":
    main()

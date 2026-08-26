"""
Устанавливает зависимости бота в виртуальное окружение.
Работает на Windows, Linux и macOS.

Запуск:
    python setup.py
"""

import os
import subprocess
import sys

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BOT_DIR, "venv")


def venv_python():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def main():
    if not os.path.exists(VENV_DIR):
        print("Создаю виртуальное окружение...")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)

    print("Устанавливаю зависимости...")
    subprocess.run(
        [venv_python(), "-m", "pip", "install", "-r",
         os.path.join(BOT_DIR, "requirements.txt")],
        check=True,
    )

    print()
    print("Готово! Дальше:")
    print("1. Открой config.py и впиши свой BOT_TOKEN, MC_HOST, MC_PORT")
    print("2. Запусти бота командой:")
    print(f"   {venv_python()} {os.path.join(BOT_DIR, 'bot.py')}")


if __name__ == "__main__":
    main()

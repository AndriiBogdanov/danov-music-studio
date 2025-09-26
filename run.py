import os
import sys
import subprocess
from pathlib import Path

def main():
    # Получаем путь к текущей директории
    project_dir = Path(__file__).parent.absolute()
    
    # Активируем виртуальное окружение
    venv_path = project_dir / "venv"
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"
    
    if not python_path.exists():
        print("❌ Виртуальное окружение не найдено!")
        print("Создайте виртуальное окружение: python -m venv venv")
        return
    
    print("🚀 Запускаем Danov Music Studio...")
    print(f"📍 Проект: {project_dir}")
    print(f"🐍 Python: {python_path}")
    
    try:
        # Запускаем Django сервер
        subprocess.run([python_path, 'manage.py', 'runserver', '0.0.0.0:80'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    main() 
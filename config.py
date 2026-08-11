import os
from pathlib import Path


# Directorio base del proyecto.
BASE_DIR = Path(__file__).resolve().parent


def _load_env_file():
    """
    Carga las variables del archivo .env si existe.
    No requiere instalar librerías externas.

    Este archivo .env solo existe en tu PC y está en .gitignore,
    así que nunca se subirá a GitHub.
    """
    env_file = BASE_DIR / ".env"
    if not env_file.is_file():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


_load_env_file()


# Token del bot.
# En tu PC se lee desde el archivo .env (variable TELEGRAM_BOT_TOKEN).
# En Render se leerá desde la variable de entorno TELEGRAM_BOT_TOKEN.
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


# Cadena de conexión a la base de datos PostgreSQL (Supabase).
# En tu PC se lee desde el archivo .env (variable DATABASE_URL).
# En Render se leerá desde la variable de entorno DATABASE_URL.
DATABASE_URL = os.environ.get("DATABASE_URL", "")


# Archivo de base de datos local (ya no se usa, pero se mantiene por compatibilidad).
DATABASE_FILE = BASE_DIR / "escape_room.db"


# Borrar los mensajes de texto que envía el jugador.
DELETE_USER_MESSAGES = True
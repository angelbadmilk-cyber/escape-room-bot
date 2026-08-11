import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import BotCommand, Update
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import TOKEN
from engine import database, handlers, photo_renderer
from engine.handlers import (
    button_callback,
    error_handler,
    help_command,
    restart_command,
    start,
    text_handler,
)
from engine.state_handlers import (
    state_action_callback,
    state_callback,
    state_command,
)
from engine.hint_handlers import hint_callback
from engine.tutorial_handlers import howto_callback, howto_command
from engine.lock_handlers import lock_callback
from engine.reset_handlers import reset_current_game_command
from engine.flag_handlers import flag_callback
from engine.command_list_handlers import commands_list_command
from engine.game_menu_handlers import game_info_callback, start_game_callback
from engine.inventory_handlers import inventory_show_callback, inventory_back_callback
from engine.diary_handlers import (
    diary_back_callback,
    diary_get_callback,
    diary_read_callback,
    diary_show_callback,
)


handlers._render_photo = photo_renderer.render_photo


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def _start_ping_server():
    class PingHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")

        def log_message(self, format, *args):
            pass

    port = int(os.environ.get("PORT", "10000"))

    def serve():
        try:
            server = HTTPServer(("0.0.0.0", port), PingHandler)
            logger.info("Servidor de ping iniciado en el puerto %s", port)
            server.serve_forever()
        except Exception as e:
            logger.warning("El servidor de ping no pudo iniciar: %s", e)

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()


async def _preload_progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Carga el progreso del jugador desde la base de datos ANTES de que
    cualquier otro handler procese el mensaje o el botón.
    Esto garantiza que, tras un redeploy, el inventario y la habitación
    se recuperen automáticamente desde Supabase.
    """
    await handlers._load_progress_from_db(update, context)


async def post_init(application: Application) -> None:
    await database.init_db()

    commands = [
        BotCommand("start", "Menú principal"),
        BotCommand("como_jugar", "Instrucciones básicas"),
        BotCommand("estado", "Ver partida y objetos"),
        BotCommand("comandos", "Ver todos los comandos"),
        BotCommand("ayuda", "Ayuda general"),
        BotCommand("reiniciar_juego", "Reiniciar aventura actual"),
        BotCommand("reiniciar", "Borrar todo el progreso"),
    ]

    try:
        await application.bot.set_my_commands(commands)
        logger.info("Menú de comandos de Telegram configurado.")
    except TelegramError:
        logger.warning("No se pudo configurar el menú de comandos de Telegram.")


def main() -> None:
    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    # PRECARGA: corre en el grupo -1 (antes que todos los demás handlers).
    # Recupera el progreso desde Supabase en cada interacción.
    application.add_handler(
        CallbackQueryHandler(_preload_progress),
        group=-1,
    )
    application.add_handler(
        MessageHandler(filters.ALL, _preload_progress),
        group=-1,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("reiniciar", restart_command))
    application.add_handler(CommandHandler("reiniciar_juego", reset_current_game_command))
    application.add_handler(CommandHandler("estado", state_command))
    application.add_handler(CommandHandler("como_jugar", howto_command))
    application.add_handler(CommandHandler("comandos", commands_list_command))

    application.add_handler(CallbackQueryHandler(state_callback, pattern="^menu:state$"))
    application.add_handler(CallbackQueryHandler(state_action_callback, pattern=r"^state:"))
    application.add_handler(CallbackQueryHandler(howto_callback, pattern="^menu:howto$"))
    application.add_handler(CallbackQueryHandler(hint_callback, pattern="^hint$"))
    application.add_handler(CallbackQueryHandler(inventory_show_callback, pattern=r"^inv:show$"))
    application.add_handler(CallbackQueryHandler(inventory_back_callback, pattern=r"^inv:back$"))

    application.add_handler(CallbackQueryHandler(diary_get_callback, pattern=r"^diary:get:"))
    application.add_handler(CallbackQueryHandler(diary_read_callback, pattern=r"^diary:read:"))
    application.add_handler(CallbackQueryHandler(diary_show_callback, pattern=r"^diary:show$"))
    application.add_handler(CallbackQueryHandler(diary_back_callback, pattern=r"^diary:back$"))

    application.add_handler(CallbackQueryHandler(flag_callback, pattern=r"^flag:"))
    application.add_handler(CallbackQueryHandler(lock_callback, pattern=r"^lock:"))
    application.add_handler(CallbackQueryHandler(game_info_callback, pattern=r"^choose:"))
    application.add_handler(CallbackQueryHandler(start_game_callback, pattern=r"^startgame:"))

    application.add_handler(CallbackQueryHandler(button_callback))

    application.add_handler(MessageHandler(filters.TEXT, text_handler))

    application.add_error_handler(error_handler)

    if os.environ.get("RENDER_EXTERNAL_URL"):
        _start_ping_server()

    logger.info("Bot iniciado en modo polling.")

    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
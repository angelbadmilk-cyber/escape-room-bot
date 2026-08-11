import logging
import os

from telegram import BotCommand
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
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

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ayuda", help_command))

    application.add_handler(CommandHandler("reiniciar", restart_command))

    application.add_handler(CommandHandler("reiniciar_juego", reset_current_game_command))

    application.add_handler(CommandHandler("estado", state_command))

    application.add_handler(CommandHandler("como_jugar", howto_command))

    application.add_handler(CommandHandler("comandos", commands_list_command))

    application.add_handler(
        CallbackQueryHandler(
            state_callback,
            pattern="^menu:state$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            state_action_callback,
            pattern=r"^state:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            howto_callback,
            pattern="^menu:howto$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            hint_callback,
            pattern="^hint$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            inventory_show_callback,
            pattern=r"^inv:show$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            inventory_back_callback,
            pattern=r"^inv:back$"
        )
    )

    # Handlers del diario coleccionable.
    application.add_handler(
        CallbackQueryHandler(
            diary_get_callback,
            pattern=r"^diary:get:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            diary_read_callback,
            pattern=r"^diary:read:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            diary_show_callback,
            pattern=r"^diary:show$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            diary_back_callback,
            pattern=r"^diary:back$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            flag_callback,
            pattern=r"^flag:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            lock_callback,
            pattern=r"^lock:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            game_info_callback,
            pattern=r"^choose:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            start_game_callback,
            pattern=r"^startgame:"
        )
    )

    application.add_handler(CallbackQueryHandler(button_callback))

    application.add_handler(
        MessageHandler(
            filters.TEXT,
            text_handler,
        )
    )

    application.add_error_handler(error_handler)

    logger.info("Bot iniciado en modo polling.")

    application.run_polling(
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
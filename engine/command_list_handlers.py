from telegram import Update
from telegram.ext import ContextTypes

from engine.handlers import (
    _edit_or_send_ui_message,
    _try_delete_message,
)
from engine.keyboards import back_to_menu_keyboard


COMMANDS_TEXT = (
    "📜 Comandos disponibles\n\n"
    "/start - Mostrar menú principal\n"
    "/como_jugar - Ver instrucciones básicas\n"
    "/estado - Ver aventura actual, habitación y objetos\n"
    "/comandos - Ver esta lista de comandos\n"
    "/ayuda - Ver ayuda general\n"
    "/help - Ver ayuda general\n"
    "/reiniciar_juego - Reiniciar solo la aventura actual\n"
    "/reiniciar - Borrar todo el progreso\n\n"
    "Consejo:\n"
    "En móviles, también puedes pulsar el botón de comandos de Telegram "
    "para ver esta lista."
)


async def commands_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /comandos.

    Muestra una lista con todos los comandos disponibles.
    """

    await _try_delete_message(context, update.effective_message)

    await _edit_or_send_ui_message(
        update,
        context,
        COMMANDS_TEXT,
        back_to_menu_keyboard(),
    )
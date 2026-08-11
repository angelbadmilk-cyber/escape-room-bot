from telegram import Update
from telegram.ext import ContextTypes

from engine.handlers import (
    _edit_or_send_ui_message,
    _edit_query_ui,
    _try_delete_message,
)
from engine.keyboards import back_to_menu_keyboard


HOW_TO_PLAY_TEXT = (
    "📖 Cómo jugar\n\n"
    "Este bot funciona principalmente con botones.\n\n"
    "1. Pulsa 🎮 Jugar para continuar tu última aventura.\n"
    "2. Pulsa 🧭 Elegir juego si quieres cambiar de aventura.\n"
    "3. En algunas habitaciones tendrás que escribir códigos.\n"
    "4. Cuando un puzle te pida un código, escribe el código y envíalo.\n"
    "5. Usa 🎒 Estado para ver objetos y marcas conseguidas.\n"
    "6. Si una habitación tiene 💡 Pista, puedes pulsarla para recibir ayuda.\n\n"
    "Comandos útiles:\n"
    "/start - Mostrar menú principal\n"
    "/estado - Ver tu estado actual\n"
    "/como_jugar - Ver estas instrucciones\n"
    "/reiniciar - Borrar todo tu progreso\n\n"
    "Consejo:\n"
    "El bot intenta editar siempre el mismo mensaje para no llenar el chat."
)


async def howto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /como_jugar.

    Muestra instrucciones básicas del bot.
    """

    await _try_delete_message(context, update.effective_message)

    await _edit_or_send_ui_message(
        update,
        context,
        HOW_TO_PLAY_TEXT,
        back_to_menu_keyboard(),
    )


async def howto_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Botón 📖 Cómo jugar.

    Muestra instrucciones básicas del bot.
    """

    query = update.callback_query

    await query.answer()

    await _edit_query_ui(
        query,
        context,
        HOW_TO_PLAY_TEXT,
        back_to_menu_keyboard(),
    )
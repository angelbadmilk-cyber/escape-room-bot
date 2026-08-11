from telegram import Update
from telegram.ext import ContextTypes

from engine import database
from engine.handlers import (
    _edit_or_send_ui_message,
    _load_progress_from_db,
    _try_delete_message,
)
from engine.keyboards import back_to_menu_keyboard
from games.registry import get_game_by_id


async def reset_current_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /reiniciar_juego.

    Borra solo el progreso del juego actual.
    """

    await _try_delete_message(context, update.effective_message)

    await _load_progress_from_db(update, context)

    if context.user_data is None:
        await _edit_or_send_ui_message(
            update,
            context,
            "No se pudo cargar la sesión.",
            back_to_menu_keyboard(),
        )
        return

    game_id = context.user_data.get("current_game")

    if not game_id:
        await _edit_or_send_ui_message(
            update,
            context,
            "No estás jugando ninguna aventura.\n\n"
            "Usa 🎮 Jugar o 🧭 Elegir juego para empezar.",
            back_to_menu_keyboard(),
        )
        return

    game = get_game_by_id(game_id)

    if game:
        game_title = game.get("title", game_id)
    else:
        game_title = game_id

    user = update.effective_user

    if user:
        await database.clear_game_progress(user.id, game_id)

    # Limpiamos la sesión actual.
    context.user_data.pop("current_game", None)
    context.user_data.pop("current_room", None)
    context.user_data.pop("current_flags", None)
    context.user_data.pop("waiting_code", None)
    context.user_data.pop("progress_loaded", None)

    text = (
        f"🗑️ Has reiniciado: {game_title}\n\n"
        "El progreso de las demás aventuras se conserva."
    )

    await _edit_or_send_ui_message(
        update,
        context,
        text,
        back_to_menu_keyboard(),
    )
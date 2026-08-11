from telegram import Update
from telegram.ext import ContextTypes

from engine import game_manager


async def hint_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Botón 💡 Pista.

    Muestra una pista en una ventana emergente.
    """

    query = update.callback_query

    if context.user_data is None:
        await query.answer(
            "No hay ninguna sesión activa.",
            show_alert=True,
        )
        return

    game_id = context.user_data.get("current_game")
    room_id = context.user_data.get("current_room")

    if not game_id or not room_id:
        await query.answer(
            "No hay ninguna partida activa.",
            show_alert=True,
        )
        return

    room = game_manager.get_room(game_id, room_id)

    if not room:
        await query.answer(
            "No se pudo cargar la habitación.",
            show_alert=True,
        )
        return

    hint = room.get("hint")

    if not hint:
        await query.answer(
            "No hay pista para esta habitación.",
            show_alert=False,
        )
        return

    await query.answer(
        f"💡 Pista:\n{hint}",
        show_alert=True,
    )
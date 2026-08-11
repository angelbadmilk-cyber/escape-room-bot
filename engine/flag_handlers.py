from telegram import Update
from telegram.ext import ContextTypes

from engine import database, game_manager, handlers
from engine.items import (
    get_item_description,
    get_item_image,
    get_item_name,
)
from games.registry import get_game_by_id


async def flag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Botón que da un flag al jugador.
    """

    query = update.callback_query

    if context.user_data is None:
        await query.answer("No se pudo cargar la sesión.", show_alert=True)
        return

    data = query.data or ""

    if ":" not in data:
        await query.answer("Acción no reconocida.", show_alert=True)
        return

    flag = data.split(":", 1)[1]

    if not flag:
        await query.answer("Acción no reconocida.", show_alert=True)
        return

    user = query.from_user
    game_id = context.user_data.get("current_game")
    room_id = context.user_data.get("current_room")

    if not user or not game_id or not room_id:
        await query.answer("No hay ninguna partida activa.", show_alert=True)
        return

    item_name = get_item_name(flag)
    description = get_item_description(flag)

    current_flags = context.user_data.get("current_flags")
    if not isinstance(current_flags, list):
        current_flags = []

    game = get_game_by_id(game_id)
    room = game_manager.get_room(game_id, room_id)

    if not game or not room:
        await query.answer("No se pudo cargar la habitación.", show_alert=True)
        return

    if flag in current_flags:
        await query.answer(f"Ya tienes: {item_name}", show_alert=False)
        return

    await database.set_flag(user.id, game_id, flag)
    current_flags.append(flag)
    context.user_data["current_flags"] = current_flags

    flags_list = context.user_data.get("current_flags")
    if not isinstance(flags_list, list):
        flags_list = []
    keyboard = game_manager.build_room_keyboard(game, room, flags_list)

    image_url = get_item_image(flag)

    caption = f"✅ Has obtenido: {item_name}"
    if description:
        caption += f"\n\n{description}"

    chat_id = query.message.chat_id if query.message else None

    if image_url and not image_url.startswith("PEGA_AQUI"):
        await handlers._render_photo(
            context,
            chat_id,
            image_url,
            caption,
            keyboard,
            fallback_message=query.message,
        )
    else:
        await handlers._render_text(
            context,
            chat_id,
            caption,
            keyboard,
            fallback_message=query.message,
        )
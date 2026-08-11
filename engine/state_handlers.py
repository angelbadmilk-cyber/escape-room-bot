from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from engine import database, game_manager
from engine.handlers import (
    _edit_or_send_ui_message,
    _edit_query_ui,
    _get_current_flags,
    _load_progress_from_db,
    _try_delete_message,
)
from engine.items import ITEMS_ORDER, TOTAL_ITEMS
from games.registry import get_game_by_id


# Nombres visibles para algunos flags conocidos.
FLAG_LABELS = {
    "antorcha": "🔥 Antorcha",
    "linterna": "🔦 Linterna",
    "llave_hueso": "🗝️ Llave de hueso",
    "sello_real": "👑 Sello real",
    "vela_encendida": "🕯️ Vela encendida",
}


def _format_flag(flag: str) -> str:
    """
    Convierte un flag técnico en un texto más legible.
    """

    if flag in FLAG_LABELS:
        return FLAG_LABELS[flag]

    return flag.replace("_", " ").capitalize()


def _get_current_game_title(context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Devuelve el título del juego actual.
    """

    if context.user_data is None:
        return "Desconocido"

    game_id = context.user_data.get("current_game")

    if not game_id:
        return "Desconocido"

    game = get_game_by_id(game_id)

    if game:
        return game.get("title", game_id)

    return game_id


def _state_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    """
    Crea el teclado de la pantalla Estado.
    """

    keyboard = []

    keyboard.append(
        [
            InlineKeyboardButton(
                "🎒 Ver objetos",
                callback_data="inv:show"
            )
        ]
    )

    if context.user_data is not None and context.user_data.get("current_game"):
        keyboard.append(
            [
                InlineKeyboardButton(
                    "🔄 Reiniciar aventura",
                    callback_data="state:reset"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                "⬅️ Volver al menú",
                callback_data="menu:main"
            )
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def build_state_text(context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Construye el texto de la pantalla de estado.
    """

    if context.user_data is None:
        return (
            "🎒 Estado\n\n"
            "No hay información disponible."
        )

    game_id = context.user_data.get("current_game")
    room_id = context.user_data.get("current_room")

    if not game_id:
        return (
            "🎒 Estado\n\n"
            "No estás jugando ninguna aventura.\n\n"
            "Usa 🎮 Jugar o 🧭 Elegir juego para empezar."
        )

    game = get_game_by_id(game_id)

    if game:
        game_title = game.get("title", game_id)
    else:
        game_title = game_id

    room_title = "Desconocida"

    if room_id:
        room = game_manager.get_room(game_id, room_id)

        if room:
            room_title = room.get("title", room_id)
        else:
            room_title = room_id

    flags = _get_current_flags(context)

    if flags:
        flag_lines = []

        for flag in flags:
            flag_lines.append(f"- {_format_flag(flag)}")

        flags_text = "\n".join(flag_lines)
    else:
        flags_text = "- Sin objetos"

    owned = [f for f in ITEMS_ORDER if f in flags]

    return (
        "🎒 Estado\n\n"
        f"Aventura: {game_title}\n"
        f"Habitación: {room_title}\n\n"
        f"Objetos: {len(owned)}/{TOTAL_ITEMS}\n\n"
        "Objetos y marcas:\n"
        f"{flags_text}"
    )


async def state_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /estado.
    """

    await _try_delete_message(context, update.effective_message)

    await _load_progress_from_db(update, context)

    text = build_state_text(context)
    keyboard = _state_keyboard(context)

    await _edit_or_send_ui_message(
        update,
        context,
        text,
        keyboard,
    )


async def state_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Botón 🎒 Estado.
    """

    query = update.callback_query

    await query.answer()

    await _load_progress_from_db(query, context)

    text = build_state_text(context)
    keyboard = _state_keyboard(context)

    await _edit_query_ui(
        query,
        context,
        text,
        keyboard,
    )


async def state_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Procesa acciones dentro de la pantalla Estado.
    """

    query = update.callback_query

    await query.answer()

    await _load_progress_from_db(query, context)

    data = query.data or ""

    if data == "state:reset":
        if context.user_data is None or not context.user_data.get("current_game"):
            await _edit_query_ui(
                query,
                context,
                "No estás jugando ninguna aventura.",
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⬅️ Volver al menú",
                                callback_data="menu:main"
                            )
                        ]
                    ]
                ),
            )
            return

        game_title = _get_current_game_title(context)

        text = (
            f"¿Seguro que quieres reiniciar {game_title}?\n\n"
            "Se borrará solo el progreso de esta aventura.\n"
            "Las demás aventuras se conservarán."
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Sí, reiniciar",
                        callback_data="state:reset_confirm"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Cancelar",
                        callback_data="state:cancel"
                    )
                ],
            ]
        )

        await _edit_query_ui(query, context, text, keyboard)
        return

    elif data == "state:reset_confirm":
        if context.user_data is None:
            await _edit_query_ui(
                query,
                context,
                "No se pudo cargar la sesión.",
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⬅️ Volver al menú",
                                callback_data="menu:main"
                            )
                        ]
                    ]
                ),
            )
            return

        game_id = context.user_data.get("current_game")

        if not game_id:
            await _edit_query_ui(
                query,
                context,
                "No estás jugando ninguna aventura.",
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⬅️ Volver al menú",
                                callback_data="menu:main"
                            )
                        ]
                    ]
                ),
            )
            return

        game_title = _get_current_game_title(context)

        user = query.from_user

        if user:
            await database.clear_game_progress(user.id, game_id)

        context.user_data.pop("current_game", None)
        context.user_data.pop("current_room", None)
        context.user_data.pop("current_flags", None)
        context.user_data.pop("waiting_code", None)
        context.user_data.pop("progress_loaded", None)

        text = (
            f"🗑️ Has reiniciado: {game_title}\n\n"
            "El progreso de las demás aventuras se conserva."
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Volver al menú",
                        callback_data="menu:main"
                    )
                ]
            ]
        )

        await _edit_query_ui(query, context, text, keyboard)
        return

    elif data == "state:cancel":
        text = build_state_text(context)
        keyboard = _state_keyboard(context)

        await _edit_query_ui(query, context, text, keyboard)
        return

    else:
        text = build_state_text(context)
        keyboard = _state_keyboard(context)

        await _edit_query_ui(query, context, text, keyboard)
        return
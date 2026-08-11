from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from engine.handlers import (
    _clear_waiting_code,
    _edit_query_ui,
    _load_game_into_context,
    _render_photo_for_query,
    _show_room_from_query,
)
from games.registry import get_game_by_code


def _game_info_keyboard(game_code: str) -> InlineKeyboardMarkup:
    """
    Crea el teclado de la ficha de información de un juego.
    """

    keyboard = [
        [
            InlineKeyboardButton(
                "▶️ Jugar",
                callback_data=f"startgame:{game_code}"
            )
        ],
        [
            InlineKeyboardButton(
                "🧭 Elegir juego",
                callback_data="menu:games"
            )
        ],
        [
            InlineKeyboardButton(
                "🏰 Menú principal",
                callback_data="menu:main"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def _build_game_info_text(game: dict) -> str:
    """
    Construye el texto de la ficha del juego.
    """

    title = game.get("title", "Juego sin título")
    theme = game.get("theme", "Tema desconocido")
    description = game.get(
        "description",
        "Este juego todavía no tiene descripción."
    )

    return (
        f"🎮 {title}\n\n"
        f"{description}\n\n"
        f"Tema: {theme}"
    )


async def game_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra la ficha de información de un juego.

    Si el juego tiene cover_url, muestra una imagen.
    Si no tiene imagen, muestra solo texto.

    Se activa con callback_data:
    choose:<code>
    """

    query = update.callback_query

    await query.answer()

    data = query.data or ""

    if ":" not in data:
        await _edit_query_ui(
            query,
            context,
            "⚠️ No se pudo encontrar el juego.",
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

    game_code = data.split(":", 1)[1]

    game = get_game_by_code(game_code)

    if not game:
        await _edit_query_ui(
            query,
            context,
            "⚠️ No se pudo encontrar el juego.",
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

    text = _build_game_info_text(game)
    keyboard = _game_info_keyboard(game_code)

    cover_url = game.get("cover_url")

    if cover_url:
        await _render_photo_for_query(
            query,
            context,
            cover_url,
            text,
            keyboard,
        )
    else:
        await _edit_query_ui(query, context, text, keyboard)


async def start_game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Empieza o reanuda un juego desde su ficha de información.

    Se activa con callback_data:
    startgame:<code>
    """

    query = update.callback_query

    await query.answer()

    data = query.data or ""

    if ":" not in data:
        await _edit_query_ui(
            query,
            context,
            "⚠️ No se pudo iniciar el juego.",
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

    game_code = data.split(":", 1)[1]

    game = get_game_by_code(game_code)

    if not game:
        await _edit_query_ui(
            query,
            context,
            "⚠️ No se pudo iniciar el juego.",
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

    if context.user_data is None:
        await _edit_query_ui(
            query,
            context,
            "⚠️ No se pudo cargar la sesión.",
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

    _clear_waiting_code(context)

    game_id = game.get("id")
    user = query.from_user

    if not user or not game_id:
        await _edit_query_ui(
            query,
            context,
            "⚠️ No se pudo iniciar el juego.",
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

    loaded = await _load_game_into_context(context, user.id, game_id)

    if not loaded:
        await _edit_query_ui(
            query,
            context,
            "⚠️ No se pudo iniciar el juego.",
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

    current_game = context.user_data.get("current_game")
    current_room = context.user_data.get("current_room")

    if current_game and current_room:
        await _show_room_from_query(query, context, current_game, current_room)
    else:
        await _edit_query_ui(
            query,
            context,
            "⚠️ No se pudo iniciar el juego.",
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
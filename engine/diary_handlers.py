from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from engine import database, handlers
from engine.diary import (
    DIARY_ORDER,
    get_diary_text,
    get_diary_title,
    is_diary_page,
)


PARSE_MODE = "HTML"


def _get_flags(context):
    if context.user_data is None:
        return []
    flags = context.user_data.get("current_flags")
    if isinstance(flags, list):
        return flags
    return []


async def _back_to_room(query, context) -> None:
    game_id = context.user_data.get("current_game") if context.user_data else None
    room_id = context.user_data.get("current_room") if context.user_data else None
    if game_id and room_id:
        await handlers._show_room_from_query(query, context, game_id, room_id)
    else:
        await handlers._edit_query_ui(
            query,
            context,
            "Para jugar, usa /start.",
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("🏰 Menú", callback_data="menu:main")]]
            ),
        )


async def diary_get_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    El jugador encuentra una página de diario.
    """
    query = update.callback_query
    await query.answer()

    if context.user_data is None:
        return

    data = query.data or ""
    parts = data.split(":", 2)
    if len(parts) < 3:
        return
    flag = parts[2]

    if not is_diary_page(flag):
        return

    user = query.from_user
    game_id = context.user_data.get("current_game")
    room_id = context.user_data.get("current_room")

    if not user or not game_id or not room_id:
        return

    flags = _get_flags(context)

    if flag not in flags:
        await database.set_flag(user.id, game_id, flag)
        flags.append(flag)
        context.user_data["current_flags"] = flags

    text = (
        f"<b>{get_diary_title(flag)}</b>\n\n"
        f"<i>{get_diary_text(flag)}</i>\n\n"
        "📖 <b>Has añadido esta página a tu diario.</b>"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📖 Abrir el diario", callback_data="diary:show")],
            [InlineKeyboardButton("⬅️ Volver", callback_data="diary:back")],
        ]
    )

    await handlers._edit_query_ui(query, context, text, keyboard)


async def diary_show_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra el índice del diario con las páginas encontradas.
    """
    query = update.callback_query
    await query.answer()

    flags = _get_flags(context)
    collected = [f for f in DIARY_ORDER if f in flags]

    rows = []

    if not collected:
        text = (
            "📖 <b>Diario</b>\n\n"
            "<i>Aún no has encontrado ninguna página.\n\n"
            "Explora el castillo: las paredes, las torres y las piedras "
            "guardan los secretos de quienes vivieron aquí.</i>"
        )
    else:
        text = (
            f"📖 <b>Diario</b>\n\n"
            f"Páginas encontradas: <b>{len(collected)}/{len(DIARY_ORDER)}</b>\n\n"
            "Pulsa una página para leerla."
        )
        for flag in collected:
            rows.append(
                [InlineKeyboardButton(get_diary_title(flag), callback_data=f"diary:read:{flag}")]
            )

    rows.append([InlineKeyboardButton("⬅️ Volver", callback_data="diary:back")])

    keyboard = InlineKeyboardMarkup(rows)
    await handlers._edit_query_ui(query, context, text, keyboard)


async def diary_read_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Muestra el texto de una página concreta.
    """
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    parts = data.split(":", 2)
    if len(parts) < 3:
        return
    flag = parts[2]

    if not is_diary_page(flag):
        return

    text = (
        f"<b>{get_diary_title(flag)}</b>\n\n"
        f"<i>{get_diary_text(flag)}</i>"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📖 Volver al diario", callback_data="diary:show")],
            [InlineKeyboardButton("⬅️ Volver a la habitación", callback_data="diary:back")],
        ]
    )

    await handlers._edit_query_ui(query, context, text, keyboard)


async def diary_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Vuelve a la habitación actual.
    """
    query = update.callback_query
    await query.answer()
    await _back_to_room(query, context)
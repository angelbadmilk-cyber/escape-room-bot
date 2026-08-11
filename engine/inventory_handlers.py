from telegram import Update
from telegram.ext import ContextTypes

from engine import handlers
from engine.items import ITEMS_ORDER, TOTAL_ITEMS, get_item
from engine.keyboards import inventory_keyboard
from games.registry import get_game_by_id


PARSE_MODE = "HTML"


def _get_owned_items(context):
    if context.user_data is None:
        return []
    flags = context.user_data.get("current_flags") or []
    return [f for f in ITEMS_ORDER if f in flags]


def _get_chat_id(query):
    if query.message:
        return query.message.chat_id
    if query.from_user:
        return query.from_user.id
    return None


async def _show_inventory(context, chat_id, fallback_message=None):
    owned = _get_owned_items(context)

    if not owned:
        text = (
            "<b>🎒 Inventario</b>\n\n"
            "<i>Tu inventario está vacío.</i>\n\n"
            f"Objetos: <b>0/{TOTAL_ITEMS}</b>"
        )
        await handlers._render_text(
            context, chat_id, text, inventory_keyboard(), fallback_message
        )
        return

    for flag in owned:
        item = get_item(flag)
        if not item:
            continue

        caption = f"<b>{item['name']}</b>\n\n<i>{item['description']}</i>"
        image = item.get("image")
        sent = False

        if image and not image.startswith("PEGA_AQUI"):
            try:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=image,
                    caption=caption,
                    parse_mode=PARSE_MODE,
                )
                sent = True
            except Exception:
                sent = False

        if not sent:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode=PARSE_MODE,
                )
            except Exception:
                pass

    text = (
        "<b>🎒 Inventario</b>\n\n"
        f"Objetos: <b>{len(owned)}/{TOTAL_ITEMS}</b>"
    )
    await handlers._render_text(
        context, chat_id, text, inventory_keyboard(), fallback_message
    )


async def inventory_show_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = _get_chat_id(query)
    await _show_inventory(context, chat_id, query.message)


async def inventory_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    game_id = context.user_data.get("current_game") if context.user_data else None
    room_id = context.user_data.get("current_room") if context.user_data else None

    if game_id and room_id:
        await handlers._show_room_from_query(query, context, game_id, room_id)
    else:
        await handlers._edit_query_ui(
            query,
            context,
            "Para jugar, usa /start.",
            inventory_keyboard(),
        )
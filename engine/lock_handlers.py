from telegram import Update
from telegram.ext import ContextTypes

from engine.state_handlers import _format_flag


async def lock_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Botón bloqueado.

    Se muestra cuando el jugador intenta usar una opción
    para la que todavía necesita un objeto o flag.
    """

    query = update.callback_query

    data = query.data or ""

    if ":" not in data:
        await query.answer(
            "🔒 Todavía no puedes hacer eso.",
            show_alert=True,
        )
        return

    flag = data.split(":", 1)[1]

    if not flag:
        await query.answer(
            "🔒 Todavía no puedes hacer eso.",
            show_alert=True,
        )
        return

    item_name = _format_flag(flag)

    await query.answer(
        f"🔒 Todavía necesitas:\n{item_name}",
        show_alert=True,
    )
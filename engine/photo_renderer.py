import logging
from pathlib import Path

from telegram import InputMediaPhoto
from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes

from engine import handlers


logger = logging.getLogger(__name__)


# Modo de formato: HTML para que las negritas y cursivas funcionen.
PARSE_MODE = "HTML"


def _resolve_photo(photo):
    """
    Convierte la referencia de imagen en algo que Telegram entienda.
    Acepta URLs (https://...) o rutas locales de archivo.
    """
    if not photo:
        return None

    if isinstance(photo, Path):
        return photo

    text = str(photo)

    if text.startswith("http://") or text.startswith("https://"):
        return text

    path = Path(text)
    if path.is_file():
        return path

    return text


async def render_photo(context: ContextTypes.DEFAULT_TYPE, chat_id, photo_url, caption: str, keyboard, fallback_message=None) -> bool:
    """
    Envía o edita un mensaje con imagen usando formato HTML.
    """
    if not chat_id:
        return False

    photo = _resolve_photo(photo_url)

    if photo is None:
        return await handlers._render_text(context, chat_id, caption, keyboard, fallback_message)

    ui_chat_id, ui_message_id, ui_message_type = handlers._get_ui_data(context)

    if ui_message_type == "photo" and ui_chat_id == chat_id and ui_message_id:
        try:
            media = InputMediaPhoto(
                media=photo,
                caption=caption,
                parse_mode=PARSE_MODE,
            )
            await context.bot.edit_message_media(
                chat_id=ui_chat_id,
                message_id=ui_message_id,
                media=media,
                reply_markup=keyboard,
            )
            return True
        except BadRequest as error:
            if "not modified" in str(error).lower():
                return True
        except TelegramError:
            pass

    old_message_id = ui_message_id if ui_chat_id == chat_id else None

    sent_message = None
    try:
        sent_message = await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            reply_markup=keyboard,
            parse_mode=PARSE_MODE,
        )
    except TelegramError:
        logger.warning("No se pudo enviar la imagen principal.")

    if sent_message:
        handlers._set_ui_data(context, chat_id, sent_message.message_id, "photo")
        if old_message_id and old_message_id != sent_message.message_id:
            await handlers._delete_message_safe(context, chat_id, old_message_id)
        return True

    fallback_text = (
        f"{caption}\n\n"
        "⚠️ No se pudo cargar la imagen."
    )
    return await handlers._render_text(context, chat_id, fallback_text, keyboard, fallback_message)
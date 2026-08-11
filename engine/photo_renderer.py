import logging
from pathlib import Path

from telegram import InputMediaPhoto
from telegram.error import BadRequest, TelegramError


logger = logging.getLogger(__name__)


# Intentamos obtener BASE_DIR de config.
# Si no existe, usamos el directorio padre del proyecto.
try:
    from config import BASE_DIR
except ImportError:
    BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_photo(photo_source):
    """
    Convierte una fuente de imagen en algo usable por Telegram.

    Puede ser:
    - Una URL http/https
    - Una ruta local relativa al proyecto
    - Una ruta local absoluta
    - Un objeto Path
    """

    if not photo_source:
        return None

    if isinstance(photo_source, Path):
        path = photo_source

    else:
        photo_text = str(photo_source)

        if photo_text.startswith(("http://", "https://")):
            return photo_text

        path = Path(photo_text)

        if not path.is_absolute():
            path = BASE_DIR / path

    candidates = [path]

    if path.suffix:
        for extension in (".png", ".jpg", ".jpeg", ".webp"):
            candidates.append(path.with_suffix(extension))
    else:
        for extension in (".png", ".jpg", ".jpeg", ".webp"):
            candidates.append(path.with_name(path.name + extension))

    for candidate in candidates:
        try:
            if candidate.is_file():
                return candidate

        except OSError:
            continue

    return None


async def _edit_photo(context, chat_id, message_id, photo, caption: str, keyboard) -> bool:
    """
    Intenta editar un mensaje con imagen.
    """

    try:
        if isinstance(photo, Path):
            with photo.open("rb") as photo_file:
                media = InputMediaPhoto(
                    media=photo_file,
                    caption=caption,
                )

                await context.bot.edit_message_media(
                    chat_id=chat_id,
                    message_id=message_id,
                    media=media,
                    reply_markup=keyboard,
                )

        else:
            media = InputMediaPhoto(
                media=photo,
                caption=caption,
            )

            await context.bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=media,
                reply_markup=keyboard,
            )

        return True

    except BadRequest as error:
        if "not modified" in str(error).lower():
            return True

        logger.warning("No se pudo editar la imagen: %s", error)

    except TelegramError as error:
        logger.warning("Error de Telegram al editar la imagen: %s", error)

    except OSError as error:
        logger.warning("No se pudo leer la imagen local: %s", error)

    return False


async def _send_photo(context, chat_id, photo, caption: str, keyboard):
    """
    Envía un mensaje con imagen.
    """

    try:
        if isinstance(photo, Path):
            with photo.open("rb") as photo_file:
                return await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=caption,
                    reply_markup=keyboard,
                )

        else:
            return await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                reply_markup=keyboard,
            )

    except TelegramError as error:
        logger.warning("No se pudo enviar la imagen: %s", error)

    except OSError as error:
        logger.warning("No se pudo leer la imagen local: %s", error)

    return None


async def render_photo(context, chat_id, photo_source, caption: str, keyboard, fallback_message=None) -> bool:
    """
    Muestra o edita un mensaje con imagen.

    Si la imagen no se puede cargar, muestra texto como respaldo.
    """

    if not chat_id:
        return False

    photo = _resolve_photo(photo_source)

    if not photo:
        fallback_text = (
            f"{caption}\n\n"
            "⚠️ No se pudo cargar la imagen."
        )

        return await _render_text(
            context,
            chat_id,
            fallback_text,
            keyboard,
            fallback_message,
        )

    ui_chat_id, ui_message_id, ui_message_type = _get_ui_data(context)

    if ui_message_type == "photo" and ui_chat_id == chat_id and ui_message_id:
        edited = await _edit_photo(
            context,
            ui_chat_id,
            ui_message_id,
            photo,
            caption,
            keyboard,
        )

        if edited:
            return True

    old_message_id = ui_message_id if ui_chat_id == chat_id else None

    sent_message = await _send_photo(
        context,
        chat_id,
        photo,
        caption,
        keyboard,
    )

    if sent_message:
        _set_ui_data(
            context,
            chat_id,
            sent_message.message_id,
            "photo",
        )

        if old_message_id and old_message_id != sent_message.message_id:
            await _delete_message_safe(
                context,
                chat_id,
                old_message_id,
            )

        return True

    fallback_text = (
        f"{caption}\n\n"
        "⚠️ No se pudo cargar la imagen."
    )

    return await _render_text(
        context,
        chat_id,
        fallback_text,
        keyboard,
        fallback_message,
    )


# Importamos estas funciones de handlers al final para evitar ciclos.
from engine.handlers import (
    _delete_message_safe,
    _get_ui_data,
    _render_text,
    _set_ui_data,
)
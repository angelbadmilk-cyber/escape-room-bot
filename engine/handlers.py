import asyncio
import logging
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes

from config import DELETE_USER_MESSAGES
from engine import database, game_manager
from engine.keyboards import (
    main_menu_keyboard,
    back_to_menu_keyboard,
    game_selection_keyboard,
)
from engine.items import (
    get_item_description,
    get_item_image,
    get_item_name,
)
from games.registry import (
    get_available_games_text,
    get_enabled_games,
    get_game_by_code,
    get_game_by_id,
)


logger = logging.getLogger(__name__)


PARSE_MODE = "HTML"


MAX_PHOTO_CAPTION = 1000


MAIN_MENU_IMAGE = "https://i.ibb.co/Kx1M8prZ/01-portada-castillo.jpg"

MAIN_MENU_TEXT = (
    "<b>🏰 CASTILLO MALDITO</b>\n\n"
    "La niebla se arrastra a tus pies.\n"
    "Las puertas del castillo se abren ante ti.\n"
    "¿Serás capaz de escapar?\n\n"
    "Usa los botones para navegar.\n\n"
    "🎮 <b>Jugar</b> - Continúa tu última partida\n"
    "🧭 <b>Elegir juego</b> - Cambia de aventura\n"
    "🎒 <b>Estado</b> - Ver tus objetos y progreso\n"
    "📖 <b>Diario</b> - Leer tus páginas encontradas\n"
    "📖 <b>Cómo jugar</b> - Instrucciones\n"
    "📊 <b>Progreso</b> - Información del progreso\n"
    "❓ <b>Ayuda</b> - Ver ayuda"
)

PROGRESS_TEXT = (
    "<b>📊 Progreso</b>\n\n"
    "Tu progreso se guarda automáticamente.\n\n"
    "Cada juego guarda su propio progreso por separado.\n\n"
    "Si quieres empezar todas las aventuras desde el principio, "
    "puedes usar el comando:\n"
    "/reiniciar"
)


def help_text() -> str:
    games_text = get_available_games_text()
    return (
        "<b>❓ Ayuda</b>\n\n"
        "Este bot está diseñado para juegos de escape room.\n\n"
        "Cuando esté completo:\n"
        "- Podrás avanzar por habitaciones.\n"
        "- Podrás usar botones para interactuar.\n"
        "- Podrás abrir pistas externas.\n"
        "- El bot guardará tu progreso.\n\n"
        "<b>Botones principales:</b>\n"
        "🎮 <b>Jugar</b> - Continúa tu última partida\n"
        "🧭 <b>Elegir juego</b> - Cambia de aventura\n"
        "🎒 <b>Estado</b> - Ver tus objetos y progreso\n"
        "📖 <b>Cómo jugar</b> - Instrucciones\n"
        "📊 <b>Progreso</b> - Información del progreso\n"
        "❓ <b>Ayuda</b> - Ver ayuda\n\n"
        f"{games_text}"
    )


def _get_user(update_or_query):
    user = getattr(update_or_query, "effective_user", None)
    if user:
        return user
    return getattr(update_or_query, "from_user", None)


def _get_ui_data(context: ContextTypes.DEFAULT_TYPE):
    if context.user_data is None:
        return None, None, None
    ui_chat_id = context.user_data.get("ui_chat_id")
    ui_message_id = context.user_data.get("ui_message_id")
    ui_message_type = context.user_data.get("ui_message_type", "text")
    return ui_chat_id, ui_message_id, ui_message_type


def _set_ui_data(context: ContextTypes.DEFAULT_TYPE, chat_id, message_id, message_type="text") -> None:
    if context.user_data is None:
        return
    if chat_id is None or message_id is None:
        return
    context.user_data["ui_chat_id"] = chat_id
    context.user_data["ui_message_id"] = message_id
    context.user_data["ui_message_type"] = message_type


def _get_current_flags(context: ContextTypes.DEFAULT_TYPE):
    if context.user_data is None:
        return []
    flags = context.user_data.get("current_flags")
    if isinstance(flags, list):
        return flags
    return []


def _clear_progress_keys(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data is None:
        return
    context.user_data.pop("current_game", None)
    context.user_data.pop("current_room", None)
    context.user_data.pop("current_flags", None)
    context.user_data.pop("progress_loaded", None)


def _clear_waiting_code(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data is None:
        return
    context.user_data.pop("waiting_code", None)


async def _castle_thinks(context: ContextTypes.DEFAULT_TYPE, chat_id) -> None:
    if not chat_id:
        return
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        await asyncio.sleep(0.9)
    except TelegramError:
        pass


async def _try_delete_message(context: ContextTypes.DEFAULT_TYPE, message) -> None:
    if not DELETE_USER_MESSAGES:
        return
    if not message:
        return
    try:
        chat = message.chat
        if chat and chat.type == "private":
            await context.bot.delete_message(
                chat_id=message.chat_id,
                message_id=message.message_id,
            )
    except TelegramError:
        pass


async def _delete_message_safe(context: ContextTypes.DEFAULT_TYPE, chat_id, message_id) -> None:
    if not chat_id or not message_id:
        return
    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
    except TelegramError:
        pass


async def _render_text(context: ContextTypes.DEFAULT_TYPE, chat_id, text: str, keyboard, fallback_message=None) -> bool:
    if not chat_id:
        return False

    ui_chat_id, ui_message_id, ui_message_type = _get_ui_data(context)

    if ui_message_type == "text" and ui_chat_id == chat_id and ui_message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=ui_chat_id,
                message_id=ui_message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=PARSE_MODE,
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
        sent_message = await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=PARSE_MODE,
        )
    except TelegramError:
        logger.warning("No se pudo enviar el mensaje de texto principal.")

    if sent_message:
        _set_ui_data(context, chat_id, sent_message.message_id, "text")
        if old_message_id and old_message_id != sent_message.message_id:
            await _delete_message_safe(context, chat_id, old_message_id)
        return True

    if fallback_message:
        try:
            sent_message = await fallback_message.reply_text(
                text=text,
                reply_markup=keyboard,
                parse_mode=PARSE_MODE,
            )
            if sent_message:
                _set_ui_data(context, chat_id, sent_message.message_id, "text")
                if old_message_id and old_message_id != sent_message.message_id:
                    await _delete_message_safe(context, chat_id, old_message_id)
                return True
        except TelegramError:
            logger.warning("Tampoco se pudo enviar el mensaje de respaldo.")

    return False


async def _render_photo(context: ContextTypes.DEFAULT_TYPE, chat_id, photo_url: str, caption: str, keyboard, fallback_message=None) -> bool:
    if not chat_id:
        return False

    if not photo_url:
        return await _render_text(context, chat_id, caption, keyboard, fallback_message)

    if len(caption) > MAX_PHOTO_CAPTION:
        try:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
            )
        except TelegramError:
            logger.warning("No se pudo enviar la imagen con texto largo.")
        return await _render_text(context, chat_id, caption, keyboard, fallback_message)

    ui_chat_id, ui_message_id, ui_message_type = _get_ui_data(context)

    if ui_message_type == "photo" and ui_chat_id == chat_id and ui_message_id:
        try:
            media = InputMediaPhoto(
                media=photo_url,
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
            photo=photo_url,
            caption=caption,
            reply_markup=keyboard,
            parse_mode=PARSE_MODE,
        )
    except TelegramError:
        logger.warning("No se pudo enviar la imagen principal.")

    if sent_message:
        _set_ui_data(context, chat_id, sent_message.message_id, "photo")
        if old_message_id and old_message_id != sent_message.message_id:
            await _delete_message_safe(context, chat_id, old_message_id)
        return True

    fallback_text = (
        f"{caption}\n\n"
        "⚠️ No se pudo cargar la imagen."
    )
    return await _render_text(context, chat_id, fallback_text, keyboard, fallback_message)


async def _edit_or_send_ui_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, keyboard) -> None:
    chat = update.effective_chat
    fallback_message = update.effective_message
    if not chat:
        return
    await _render_text(context, chat.id, text, keyboard, fallback_message)


async def _edit_query_ui(query, context: ContextTypes.DEFAULT_TYPE, text: str, keyboard) -> None:
    chat_id = None
    fallback_message = None
    if query.message:
        chat_id = query.message.chat_id
        fallback_message = query.message
    elif query.from_user:
        chat_id = query.from_user.id
    await _render_text(context, chat_id, text, keyboard, fallback_message)


async def _render_photo_for_update(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_url: str, caption: str, keyboard) -> None:
    chat = update.effective_chat
    fallback_message = update.effective_message
    if not chat:
        return
    await _render_photo(context, chat.id, photo_url, caption, keyboard, fallback_message)


async def _render_photo_for_query(query, context: ContextTypes.DEFAULT_TYPE, photo_url: str, caption: str, keyboard) -> None:
    chat_id = None
    fallback_message = None
    if query.message:
        chat_id = query.message.chat_id
        fallback_message = query.message
    elif query.from_user:
        chat_id = query.from_user.id
    await _render_photo(context, chat_id, photo_url, caption, keyboard, fallback_message)


async def _show_main_menu(update_or_query, context: ContextTypes.DEFAULT_TYPE, chat_id, fallback_message=None) -> None:
    await _render_photo(
        context,
        chat_id,
        MAIN_MENU_IMAGE,
        MAIN_MENU_TEXT,
        main_menu_keyboard(),
        fallback_message,
    )


async def _apply_room_enter_flags(context: ContextTypes.DEFAULT_TYPE, user_id: int, game_id: str, room: dict) -> None:
    if not room or not user_id or not game_id:
        return
    flags_to_set = room.get("set_flags_on_enter", [])
    if not flags_to_set:
        return
    current_flags = _get_current_flags(context)
    for flag in flags_to_set:
        await database.set_flag(user_id, game_id, flag)
        if flag not in current_flags:
            current_flags.append(flag)
    if context.user_data is not None:
        context.user_data["current_flags"] = current_flags


async def _load_game_into_context(context: ContextTypes.DEFAULT_TYPE, user_id: int, game_id: str) -> bool:
    if context.user_data is None:
        return False
    game = get_game_by_id(game_id)
    if not game or not game.get("enabled", False):
        return False
    rooms, start_room = game_manager.get_game_data(game_id)
    if not rooms:
        return False
    saved_room = await database.get_game_progress(user_id, game_id)
    if saved_room and saved_room in rooms:
        room_id = saved_room
    else:
        room_id = start_room
    flags = await database.get_flags(user_id, game_id)
    context.user_data["current_game"] = game_id
    context.user_data["current_room"] = room_id
    context.user_data["current_flags"] = flags
    return True


async def _load_progress_from_db(update_or_query, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = _get_user(update_or_query)
    if not user:
        return
    if context.user_data is None:
        return
    if context.user_data.get("progress_loaded"):
        return
    last_game_id = await database.get_last_game_id(user.id)
    if last_game_id:
        await _load_game_into_context(context, user.id, last_game_id)
    context.user_data["progress_loaded"] = True


async def _show_room_from_update(update: Update, context, game_id: str, room_id: str) -> None:
    game = get_game_by_id(game_id)
    room = game_manager.get_room(game_id, room_id)
    if not game or not room:
        text = (
            "⚠️ No se pudo cargar la habitación.\n\n"
            "Vuelve al menú principal."
        )
        keyboard = back_to_menu_keyboard()
        await _edit_or_send_ui_message(update, context, text, keyboard)
        return

    if context.user_data is not None:
        context.user_data["current_game"] = game_id
        context.user_data["current_room"] = room_id

    user = _get_user(update)
    if user:
        await database.save_progress(user.id, game_id, room_id)
        await _apply_room_enter_flags(context, user.id, game_id, room)

    chat = update.effective_chat
    if chat:
        await _castle_thinks(context, chat.id)

    text = game_manager.render_room_text(room)
    flags = _get_current_flags(context)
    keyboard = game_manager.build_room_keyboard(game, room, flags)
    image_url = room.get("image_url")

    if image_url:
        await _render_photo_for_update(update, context, image_url, text, keyboard)
    else:
        await _edit_or_send_ui_message(update, context, text, keyboard)


async def _show_room_from_query(query, context, game_id: str, room_id: str) -> None:
    game = get_game_by_id(game_id)
    room = game_manager.get_room(game_id, room_id)
    if not game or not room:
        text = (
            "⚠️ No se pudo cargar la habitación.\n\n"
            "Vuelve al menú principal."
        )
        keyboard = back_to_menu_keyboard()
        await _edit_query_ui(query, context, text, keyboard)
        return

    if context.user_data is not None:
        context.user_data["current_game"] = game_id
        context.user_data["current_room"] = room_id

    user = _get_user(query)
    if user:
        await database.save_progress(user.id, game_id, room_id)
        await _apply_room_enter_flags(context, user.id, game_id, room)

    chat_id = None
    if query.message:
        chat_id = query.message.chat_id
    elif query.from_user:
        chat_id = query.from_user.id
    await _castle_thinks(context, chat_id)

    text = game_manager.render_room_text(room)
    flags = _get_current_flags(context)
    keyboard = game_manager.build_room_keyboard(game, room, flags)
    image_url = room.get("image_url")

    if image_url:
        await _render_photo_for_query(query, context, image_url, text, keyboard)
    else:
        await _edit_query_ui(query, context, text, keyboard)


async def _handle_games_menu(query, context) -> None:
    enabled_games = get_enabled_games()
    if not enabled_games:
        text = (
            "⚠️ No hay juegos disponibles todavía.\n\n"
            "Pronto se añadirá la primera aventura."
        )
        await _edit_query_ui(query, context, text, back_to_menu_keyboard())
        return

    text = (
        "<b>🧭 Elige un juego</b>\n\n"
        "Cada aventura guarda su progreso por separado."
    )
    keyboard = game_selection_keyboard(enabled_games)
    await _edit_query_ui(query, context, text, keyboard)


async def _handle_code_request(query, context, puzzle_key: str) -> None:
    if context.user_data is None:
        await _edit_query_ui(query, context, "⚠️ No se pudo cargar la sesión.", back_to_menu_keyboard())
        return

    game_id = context.user_data.get("current_game")
    room_id = context.user_data.get("current_room")
    puzzle = None

    if game_id and room_id:
        puzzle = game_manager.get_room_puzzle(game_id, room_id, puzzle_key)

    if not puzzle:
        await _edit_query_ui(query, context, "⚠️ No se encontró el puzle.", back_to_menu_keyboard())
        return

    context.user_data["waiting_code"] = puzzle_key
    prompt = puzzle.get("prompt", "Introduce el código obtenido en el puzle.")
    text = (
        f"🔑 {prompt}\n\n"
        "Escribe el código y envíalo.\n\n"
        "Para cancelar, pulsa <i>Volver al menú</i>."
    )
    await _edit_query_ui(query, context, text, back_to_menu_keyboard())


async def _handle_choice_callback(query, context, puzzle_key: str, option: str) -> None:
    """
    Maneja los puzzles de botones (elegir una opción pulsando, sin escribir).
    """
    if context.user_data is None:
        return
    game_id = context.user_data.get("current_game")
    room_id = context.user_data.get("current_room")
    if not game_id or not room_id:
        return

    puzzle = game_manager.get_room_puzzle(game_id, room_id, puzzle_key)
    if not puzzle:
        return

    game = get_game_by_id(game_id)
    game_code = game.get("code", "") if game else ""
    back_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Volver", callback_data=f"play:{game_code}:{room_id}")]]
    )

    if game_manager.check_puzzle_code(puzzle, option):
        user = _get_user(query)
        success_flag = puzzle.get("success_flag")
        if success_flag and user:
            await database.set_flag(user.id, game_id, success_flag)
            current_flags = _get_current_flags(context)
            if success_flag not in current_flags:
                current_flags.append(success_flag)
                context.user_data["current_flags"] = current_flags

        success_room = puzzle.get("success_room")
        if success_room and game:
            new_game_id, new_room_id = game_manager.navigate_to_room(
                context.user_data, game_code, success_room
            )
            if new_game_id and new_room_id:
                await _show_room_from_query(query, context, new_game_id, new_room_id)
                return

        success_text = puzzle.get("success_text", "✅ <b>Correcto.</b>")
        await _edit_query_ui(query, context, success_text, back_keyboard)
    else:
        error_text = puzzle.get("error_text", "❌ <b>Incorrecto.</b>")
        await _edit_query_ui(query, context, error_text, back_keyboard)


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data is None:
        return

    waiting_code = context.user_data.get("waiting_code")
    user_message = update.effective_message

    if not waiting_code:
        game_id = context.user_data.get("current_game")
        room_id = context.user_data.get("current_room")

        if game_id and room_id:
            await _show_room_from_update(update, context, game_id, room_id)
            return

        await _edit_or_send_ui_message(
            update,
            context,
            "Para jugar, usa /start.",
            main_menu_keyboard(),
        )
        return

    user_code = ""
    if user_message:
        user_code = user_message.text or ""

    await _try_delete_message(context, user_message)

    game_id = context.user_data.get("current_game")
    room_id = context.user_data.get("current_room")

    if not game_id or not room_id:
        _clear_waiting_code(context)
        await _edit_or_send_ui_message(
            update,
            context,
            "No hay ninguna partida activa.\n\nUsa /start para jugar.",
            main_menu_keyboard(),
        )
        return

    puzzle = game_manager.get_room_puzzle(game_id, room_id, waiting_code)

    if not puzzle:
        _clear_waiting_code(context)
        await _edit_or_send_ui_message(
            update,
            context,
            "El puzle ya no está disponible.",
            back_to_menu_keyboard(),
        )
        return

    if game_manager.check_puzzle_code(puzzle, user_code):
        _clear_waiting_code(context)

        user = _get_user(update)

        success_flag = puzzle.get("success_flag")
        if success_flag:
            if user:
                await database.set_flag(user.id, game_id, success_flag)
                current_flags = _get_current_flags(context)
                if success_flag not in current_flags:
                    current_flags.append(success_flag)
                    context.user_data["current_flags"] = current_flags

        item_image = get_item_image(success_flag) if success_flag else None
        if item_image and not item_image.startswith("PEGA_AQUI"):
            item_name = get_item_name(success_flag)
            item_description = get_item_description(success_flag)
            caption = f"✅ <b>Has obtenido: {item_name}</b>"
            if item_description:
                caption += f"\n\n<i>{item_description}</i>"

            success_text = puzzle.get("success_text", "")
            if success_text:
                caption += f"\n\n{success_text}"

            chat = update.effective_chat
            fallback_message = update.effective_message
            if chat:
                room = game_manager.get_room(game_id, room_id)
                game = get_game_by_id(game_id)
                flags = _get_current_flags(context)
                keyboard = game_manager.build_room_keyboard(game, room, flags) if room and game else back_to_menu_keyboard()
                await _render_photo(context, chat.id, item_image, caption, keyboard, fallback_message)
                return

        success_room = puzzle.get("success_room")
        if success_room:
            game = get_game_by_id(game_id)
            if game:
                game_code = game.get("code")
                new_game_id, new_room_id = game_manager.navigate_to_room(
                    context.user_data,
                    game_code,
                    success_room,
                )
                if new_game_id and new_room_id:
                    await _show_room_from_update(update, context, new_game_id, new_room_id)
                    return

        success_text = puzzle.get("success_text", "✅ <b>Código correcto.</b>")
        await _edit_or_send_ui_message(update, context, success_text, back_to_menu_keyboard())

    else:
        error_text = puzzle.get("error_text", "❌ <b>Código incorrecto.</b>")

        room = game_manager.get_room(game_id, room_id)
        game = get_game_by_id(game_id)

        if room and game:
            room_text = game_manager.render_room_text(room)
            flags = _get_current_flags(context)
            keyboard = game_manager.build_room_keyboard(game, room, flags)

            text = (
                f"{error_text}\n\n"
                f"{room_text}\n\n"
                "<i>Introduce otro código o usa los botones para navegar.</i>"
            )

            await _edit_or_send_ui_message(update, context, text, keyboard)
        else:
            _clear_waiting_code(context)
            await _edit_or_send_ui_message(
                update,
                context,
                error_text,
                back_to_menu_keyboard(),
            )


async def _handle_play(query, context) -> None:
    if context.user_data is None:
        await _edit_query_ui(query, context, "⚠️ No se pudo cargar la sesión.", back_to_menu_keyboard())
        return

    _clear_waiting_code(context)
    await _load_progress_from_db(query, context)
    current_game = context.user_data.get("current_game")

    if current_game:
        current_info = get_game_by_id(current_game)
        if current_info and current_info.get("enabled", False):
            current_room = context.user_data.get("current_room")
            if not current_room:
                user = _get_user(query)
                if user:
                    await _load_game_into_context(context, user.id, current_game)
                    current_room = context.user_data.get("current_room")
            if current_room:
                await _show_room_from_query(query, context, current_game, current_room)
                return

    enabled_games = get_enabled_games()
    if not enabled_games:
        text = (
            "⚠️ No hay juegos disponibles todavía.\n\n"
            "Pronto se añadirá la primera aventura."
        )
        await _edit_query_ui(query, context, text, back_to_menu_keyboard())
        return

    if len(enabled_games) == 1:
        game_id = enabled_games[0][0]
        user = _get_user(query)
        if user:
            await _load_game_into_context(context, user.id, game_id)
            current_game = context.user_data.get("current_game")
            current_room = context.user_data.get("current_room")
            if current_game and current_room:
                await _show_room_from_query(query, context, current_game, current_room)
                return
        text = "⚠️ No se pudo iniciar el juego."
        await _edit_query_ui(query, context, text, back_to_menu_keyboard())
        return

    await _handle_games_menu(query, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _try_delete_message(context, update.effective_message)
    _clear_waiting_code(context)
    await _load_progress_from_db(update, context)

    chat = update.effective_chat
    if not chat:
        return

    enabled_games = get_enabled_games()
    if enabled_games:
        current_game = context.user_data.get("current_game")
        if not current_game or not get_game_by_id(current_game):
            current_game = enabled_games[0][0]

        user = _get_user(update)
        if user:
            await _load_game_into_context(context, user.id, current_game)
            current_game = context.user_data.get("current_game")
            current_room = context.user_data.get("current_room")
            if current_game and current_room:
                await _show_room_from_update(update, context, current_game, current_room)
                return

    await _show_main_menu(update, context, chat.id, update.effective_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _try_delete_message(context, update.effective_message)
    await _edit_or_send_ui_message(update, context, help_text(), back_to_menu_keyboard())


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _try_delete_message(context, update.effective_message)
    user = _get_user(update)
    if user:
        await database.clear_progress(user.id)
    _clear_progress_keys(context)
    _clear_waiting_code(context)
    text = (
        "🗑️ <b>Tu progreso se ha reiniciado.</b>\n\n"
        "Puedes volver a jugar desde el menú principal."
    )
    await _edit_or_send_ui_message(update, context, text, main_menu_keyboard())


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if context.user_data is None:
        await _edit_query_ui(query, context, "⚠️ No se pudo cargar la sesión.", back_to_menu_keyboard())
        return

    data = query.data or ""

    if data == "menu:main":
        _clear_waiting_code(context)
        chat_id = query.message.chat_id if query.message else None
        await _show_main_menu(query, context, chat_id, query.message)
        return

    elif data == "menu:play":
        await _handle_play(query, context)
        return

    elif data == "menu:games":
        await _handle_games_menu(query, context)
        return

    elif data == "menu:progress":
        text = PROGRESS_TEXT
        keyboard = back_to_menu_keyboard()
        await _edit_query_ui(query, context, text, keyboard)
        return

    elif data == "menu:help":
        text = help_text()
        keyboard = back_to_menu_keyboard()
        await _edit_query_ui(query, context, text, keyboard)
        return

    elif data.startswith("choose:"):
        _clear_waiting_code(context)
        code = data.split(":", 1)[1]
        game = get_game_by_code(code)
        if game:
            game_id = game.get("id")
            user = _get_user(query)
            if user:
                await _load_game_into_context(context, user.id, game_id)
                current_game = context.user_data.get("current_game")
                current_room = context.user_data.get("current_room")
                if current_game and current_room:
                    await _show_room_from_query(query, context, current_game, current_room)
                    return
        text = "⚠️ No se pudo encontrar el juego."
        keyboard = back_to_menu_keyboard()
        await _edit_query_ui(query, context, text, keyboard)
        return

    elif data.startswith("play:"):
        _clear_waiting_code(context)
        parts = data.split(":")
        if len(parts) == 3:
            _, code, room_id = parts
            game_id, new_room_id = game_manager.navigate_to_room(
                context.user_data,
                code,
                room_id,
            )
            if game_id and new_room_id:
                await _show_room_from_query(query, context, game_id, new_room_id)
                return
        text = "⚠️ No se pudo cargar la habitación."
        keyboard = back_to_menu_keyboard()
        await _edit_query_ui(query, context, text, keyboard)
        return

    elif data.startswith("flag:"):
        flag_name = data.split(":", 1)[1]
        await _handle_flag_callback(query, context, flag_name)
        return

    elif data.startswith("code:"):
        puzzle_key = data.split(":", 1)[1]
        await _handle_code_request(query, context, puzzle_key)
        return

    elif data.startswith("choice:"):
        parts = data.split(":", 2)
        if len(parts) == 3:
            _, puzzle_key, option = parts
            await _handle_choice_callback(query, context, puzzle_key, option)
        return

    else:
        text = (
            "⚠️ Opción no reconocida.\n\n"
            "Vuelve al menú principal para continuar."
        )
        keyboard = back_to_menu_keyboard()
        await _edit_query_ui(query, context, text, keyboard)
        return


async def _handle_flag_callback(query, context, flag_name: str) -> None:
    if context.user_data is None:
        return
    user = _get_user(query)
    game_id = context.user_data.get("current_game")
    room_id = context.user_data.get("current_room")
    if not user or not game_id or not room_id:
        return

    await database.set_flag(user.id, game_id, flag_name)
    current_flags = _get_current_flags(context)
    if flag_name not in current_flags:
        current_flags.append(flag_name)
    context.user_data["current_flags"] = current_flags
    await _show_room_from_query(query, context, game_id, room_id)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.error:
        if isinstance(context.error, BadRequest):
            error_message = str(context.error).lower()
            if "query is too old" in error_message or "query id is invalid" in error_message:
                logger.info("Consulta de botón expirada (ignorada): %s", context.error)
                return

        error_text = "".join(
            traceback.format_exception(
                type(context.error),
                context.error,
                context.error.__traceback__,
            )
        )
        logger.error(
            "Ocurrió un error: %s\n%s",
            context.error,
            error_text,
        )
    else:
        logger.error("Ocurrió un error desconocido.")
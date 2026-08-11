import importlib
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from games import registry


logger = logging.getLogger(__name__)


# Tabla de conversión de letras ASCII a caracteres góticos Unicode (Fraktur Bold).
_GOTHIC_MAP = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "\U0001d56c\U0001d56d\U0001d56e\U0001d56f\U0001d570"
    "\U0001d571\U0001d572\U0001d573\U0001d574\U0001d575"
    "\U0001d576\U0001d577\U0001d578\U0001d579\U0001d57a"
    "\U0001d57b\U0001d57c\U0001d57d\U0001d57e\U0001d57f"
    "\U0001d580\U0001d581\U0001d582\U0001d583\U0001d584"
    "\U0001d585\U0001d586\U0001d587\U0001d588\U0001d589"
    "\U0001d58a\U0001d58b\U0001d58c\U0001d58d\U0001d58e"
    "\U0001d58f\U0001d590\U0001d591\U0001d592\U0001d593"
    "\U0001d594\U0001d595\U0001d596\U0001d597\U0001d598"
    "\U0001d599\U0001d59a\U0001d59b\U0001d59c\U0001d59d"
    "\U0001d59e\U0001d59f",
)


def _to_gothic(text: str) -> str:
    """
    Convierte texto normal a caracteres góticos Unicode (Fraktur Bold).
    """
    if not text:
        return text
    return text.translate(_GOTHIC_MAP)


def get_game_data(game_id: str):
    game = registry.get_game_by_id(game_id)
    if not game:
        return None, None
    folder = game.get("folder", game_id)
    try:
        module = importlib.import_module(f"games.{folder}.rooms")
        rooms = getattr(module, "ROOMS", None)
        start_room = getattr(module, "START_ROOM", None)
        if not rooms:
            logger.error("El juego %s no tiene habitaciones definidas.", game_id)
            return None, None
        if not start_room or start_room not in rooms:
            start_room = next(iter(rooms), None)
        if not start_room:
            logger.error("No se pudo determinar la habitación inicial del juego %s.", game_id)
            return None, None
        return rooms, start_room
    except Exception:
        logger.exception("No se pudieron cargar las habitaciones del juego %s.", game_id)
        return None, None


def get_room(game_id: str, room_id: str):
    rooms, _ = get_game_data(game_id)
    if not rooms:
        return None
    return rooms.get(room_id)


def render_room_text(room: dict) -> str:
    """
    Construye el texto principal de una habitación con formato HTML.
    El título aparece en negrita, gótico y decorado para destacar más.
    """
    title = room.get("title", "Habitación")
    text = room.get("text", "")
    gothic_title = _to_gothic(title)
    return (
        f"<b>❖ {gothic_title} ❖</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{text}"
    )


def build_room_keyboard(game: dict, room: dict, flags=None) -> InlineKeyboardMarkup:
    if flags is None:
        flags = []
    flags_set = set(flags)
    game_code = game.get("code", game.get("id", ""))
    keyboard = []
    for button in room.get("buttons", []):
        label = button.get("label", "Opción")
        hide_if_flag = button.get("hide_if_flag")
        if hide_if_flag and hide_if_flag in flags_set:
            continue
        required = []
        single = button.get("requires_flag")
        if single:
            required.append(single)
        required.extend(button.get("requires_flags", []))
        if required and not all(f in flags_set for f in required):
            callback_data = f"lock:{required[0]}"
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"🔒 {label}",
                        callback_data=callback_data
                    )
                ]
            )
            continue
        if "to_room" in button:
            to_room = button["to_room"]
            callback_data = f"play:{game_code}:{to_room}"
            keyboard.append(
                [
                    InlineKeyboardButton(
                        label,
                        callback_data=callback_data
                    )
                ]
            )
        elif "callback" in button:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        label,
                        callback_data=button["callback"]
                    )
                ]
            )
        elif "url" in button:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        label,
                        url=button["url"]
                    )
                ]
            )
    if room.get("hint"):
        keyboard.append(
            [
                InlineKeyboardButton(
                    "💡 Pista",
                    callback_data="hint"
                )
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                "🎒 Objetos",
                callback_data="inv:show"
            ),
            InlineKeyboardButton(
                "🏰 Menú",
                callback_data="menu:main"
            ),
        ]
    )
    return InlineKeyboardMarkup(keyboard)


def resume_or_start_game(user_data: dict, game_id: str = None):
    enabled_games = registry.get_enabled_games()
    if not enabled_games:
        return None, None
    if game_id is None:
        current_game = user_data.get("current_game")
        if current_game:
            current_info = registry.get_game_by_id(current_game)
            if current_info and current_info.get("enabled", False):
                game_id = current_game
        if game_id is None:
            if len(enabled_games) == 1:
                game_id = enabled_games[0][0]
            else:
                return None, None
    game = registry.get_game_by_id(game_id)
    if not game or not game.get("enabled", False):
        user_data.pop("current_game", None)
        user_data.pop("current_room", None)
        return None, None
    rooms, start_room = get_game_data(game_id)
    if not rooms:
        return None, None
    current_room = user_data.get("current_room")
    if user_data.get("current_game") == game_id and current_room in rooms:
        room_id = current_room
    else:
        room_id = start_room
    user_data["current_game"] = game_id
    user_data["current_room"] = room_id
    return game_id, room_id


def navigate_to_room(user_data: dict, game_code: str, room_id: str):
    game = registry.get_game_by_code(game_code)
    if not game:
        return None, None
    game_id = game.get("id")
    rooms, _ = get_game_data(game_id)
    if not rooms or room_id not in rooms:
        return None, None
    user_data["current_game"] = game_id
    user_data["current_room"] = room_id
    return game_id, room_id


def normalize_code(code) -> str:
    if not code:
        return ""
    code = str(code).strip().upper()
    for character in (" ", "-", "_", "\n", "\t"):
        code = code.replace(character, "")
    return code


def get_room_puzzle(game_id: str, room_id: str, puzzle_key: str):
    room = get_room(game_id, room_id)
    if not room:
        return None
    puzzles = room.get("puzzles", {})
    return puzzles.get(puzzle_key)


def check_puzzle_code(puzzle: dict, user_code: str) -> bool:
    if not puzzle:
        return False
    normalized_user_code = normalize_code(user_code)
    if not normalized_user_code:
        return False
    answers = puzzle.get("answers", [])
    for answer in answers:
        if normalize_code(answer) == normalized_user_code:
            return True
    return False
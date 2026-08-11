from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🎮 Jugar", callback_data="menu:play")],
        [InlineKeyboardButton("🧭 Elegir juego", callback_data="menu:games")],
        [InlineKeyboardButton("🎒 Estado", callback_data="menu:state")],
        [InlineKeyboardButton("📖 Cómo jugar", callback_data="menu:howto")],
        [InlineKeyboardButton("📊 Progreso", callback_data="menu:progress")],
        [InlineKeyboardButton("❓ Ayuda", callback_data="menu:help")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("⬅️ Volver al menú", callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def game_selection_keyboard(enabled_games) -> InlineKeyboardMarkup:
    keyboard = []
    for game_id, game in enabled_games:
        title = game.get("title", "Juego sin título")
        code = game.get("code", game_id)
        keyboard.append([InlineKeyboardButton(title, callback_data=f"choose:{code}")])
    keyboard.append([InlineKeyboardButton("⬅️ Volver al menú", callback_data="menu:main")])
    return InlineKeyboardMarkup(keyboard)


def inventory_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("⬅️ Volver", callback_data="inv:back")],
    ]
    return InlineKeyboardMarkup(keyboard)
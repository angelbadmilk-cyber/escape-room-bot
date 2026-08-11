# Registro de juegos del bot.
#
# Para añadir imagen de portada:
# - cover_url puede ser una URL http/https


AVAILABLE_GAMES = {
    "castillo_maldito": {
        "id": "castillo_maldito",
        "code": "cm",
        "title": "Castillo Maldito",
        "folder": "castillo_maldito",
        "theme": "Castillo medieval con miedo",
        "description": (
            "Un castillo medieval envuelto en niebla, susurros y maldiciones.\n\n"
            "Explora sus habitaciones, consigue objetos, resuelve códigos "
            "y encuentra la forma de escapar antes de que el castillo te reclame."
        ),
        "cover_url": "https://i.ibb.co/Kx1M8prZ/01-portada-castillo.jpg",
        "enabled": True,
    },

    "bosque_perdido": {
        "id": "bosque_perdido",
        "code": "bp",
        "title": "El Bosque Perdido",
        "folder": "bosque_perdido",
        "theme": "Bosque misterioso",
        "description": (
            "Un bosque silencioso donde nada se mueve... excepto lo que no deberías ver.\n\n"
            "Aventura corta de prueba para experimentar con objetos y caminos ocultos."
        ),
        "cover_url": "https://telegram.org/img/t_logo.png",
        "enabled": True,
    },

    "plantilla": {
        "id": "plantilla",
        "code": "pl",
        "title": "Plantilla de juego",
        "folder": "plantilla",
        "theme": "Juego de ejemplo para crear nuevos juegos",
        "description": (
            "Plantilla básica para crear juegos nuevos.\n\n"
            "No está pensada para jugadores, sino como ejemplo técnico."
        ),
        "cover_url": "",
        "enabled": False,
    },
}


def get_available_games_text() -> str:
    """
    Devuelve un texto legible con los juegos disponibles.

    Este texto se muestra en la sección de ayuda.
    """

    lines = [
        "Juegos disponibles:",
        "",
    ]

    for game_id, game in AVAILABLE_GAMES.items():
        title = game.get("title", "Juego sin título")
        enabled = game.get("enabled", False)

        if enabled:
            status = "activo"
        else:
            status = "en construcción"

        lines.append(f"- {title} [{status}]")

    return "\n".join(lines)


def get_enabled_games():
    """
    Devuelve una lista con los juegos activos.
    """

    enabled = []

    for game_id, game in AVAILABLE_GAMES.items():
        if game.get("enabled", False):
            enabled.append((game_id, game))

    return enabled


def get_game_by_id(game_id: str):
    """
    Devuelve un juego a partir de su id.
    """

    return AVAILABLE_GAMES.get(game_id)


def get_game_by_code(code: str):
    """
    Devuelve un juego activo a partir de su código corto.
    """

    for game_id, game in AVAILABLE_GAMES.items():
        if game.get("code") == code and game.get("enabled", False):
            return game

    return None
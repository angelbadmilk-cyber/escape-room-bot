# Definición de objetos del juego Castillo Maldito.
#
# IMPORTANTE:
# - Reemplaza PEGA_AQUI_LA_URL_DE_LA_LLAVE_OXIDADA por la URL de tu imagen
#   de la llave oxidada, si ya la tienes.
# - Reemplaza PEGA_AQUI_LA_URL_DE_LA_CORONA por la URL de tu imagen
#   de la corona rota.


ITEMS = {
    "antorcha": {
        "name": "🔥 Antorcha",
        "description": "La llama ilumina la oscuridad.",
        "image": "https://i.ibb.co/RGpDwJGM/objeto-antorcha.jpg",
    },
    "llave_oxidada": {
        "name": "🗝️ Llave oxidada",
        "description": "Una vieja llave oxidada, cubierta de musgo.",
        "image": "PEGA_AQUI_LA_URL_DE_LA_LLAVE_OXIDADA",
    },
    "sello_real": {
        "name": "👑 Sello real",
        "description": "El sello real brilla con un poder antiguo.",
        "image": "https://i.ibb.co/KzrfmryN/objeto-sello-real.jpg",
    },
    "llave_hueso": {
        "name": "🗝️ Llave de hueso",
        "description": "Una llave tallada en hueso humano.",
        "image": "https://i.ibb.co/LXgh1Fqk/objeto-llave-hueso.jpg",
    },
    "corona": {
        "name": "👑 Corona rota",
        "description": "La corona del rey Aldric. Rota, pero aún valiosa.",
        "image": "PEGA_AQUI_LA_URL_DE_LA_CORONA",
    },
}


ITEMS_ORDER = ["antorcha", "llave_oxidada", "sello_real", "llave_hueso", "corona"]

TOTAL_ITEMS = len(ITEMS_ORDER)


def get_item(flag):
    return ITEMS.get(flag)


def is_item(flag):
    return flag in ITEMS


def get_item_image(flag):
    item = ITEMS.get(flag)
    if item:
        return item.get("image")
    return None


def get_item_name(flag):
    item = ITEMS.get(flag)
    if item:
        return item.get("name")
    return flag


def get_item_description(flag):
    item = ITEMS.get(flag)
    if item:
        return item.get("description")
    return ""
# Definición de objetos del juego Castillo Maldito.
#
# Si tu imagen de la llave oxidada tiene otra URL,
# reemplaza el valor de "image" en llave_oxidada.


ITEMS = {
    "antorcha": {
        "name": "🔥 Antorcha",
        "description": "La llama ilumina la oscuridad.",
        "image": "https://i.ibb.co/RGpDwJGM/objeto-antorcha.jpg",
    },
    "llave_oxidada": {
        "name": "🗝️ Llave oxidada",
        "description": "Una vieja llave oxidada, cubierta de musgo.",
        "image": "https://i.ibb.co/8D5ngYv6/objeto-llave-oxidada-patio.jpg",
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
}


ITEMS_ORDER = ["antorcha", "llave_oxidada", "sello_real", "llave_hueso"]

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
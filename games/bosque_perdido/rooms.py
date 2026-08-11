# Habitaciones del juego: El Bosque Perdido.
#
# Este juego ahora se usa para probar flags.
#
# Flags usados en esta demo:
# - linterna
#
# Botones con flags:
# - callback "flag:linterna" da el flag linterna
# - hide_if_flag oculta el botón si ya tienes el flag
# - requires_flag muestra el botón solo si tienes el flag


START_ROOM = "claro"


ROOMS = {
    "claro": {
        "title": "El claro del bosque",
        "text": (
            "Estás en un claro cubierto de hierba gris.\n\n"
            "Los árboles que te rodean son altos, torcidos y silenciosos.\n"
            "No se escucha ningún pájaro, ningún insecto, ningún viento.\n\n"
            "Entre la hierba parece haber algo medio enterrado."
        ),
        "image_url": "https://telegram.org/img/t_logo.png",
        "buttons": [
            {
                "label": "🔍 Buscar entre la hierba",
                "callback": "flag:linterna",
                "hide_if_flag": "linterna",
            },
            {
                "label": "🌲 Adentrarse en el bosque",
                "to_room": "arboles",
            },
        ],
    },

    "arboles": {
        "title": "Entre los árboles",
        "text": (
            "El sendero se estrecha.\n\n"
            "Las ramas parecen moverse lentamente por encima de ti, "
            "aunque no corre el aire.\n\n"
            "Más adelante, la oscuridad es casi total."
        ),
        "image_url": "https://telegram.org/img/t_logo.png",
        "buttons": [
            {
                "label": "⬅️ Volver al claro",
                "to_room": "claro",
            },
            {
                "label": "🔦 Iluminar el sendero",
                "to_room": "sendero_secreto",
                "requires_flag": "linterna",
            },
        ],
    },

    "sendero_secreto": {
        "title": "El sendero secreto",
        "text": (
            "La luz revela marcas en los árboles.\n\n"
            "No son marcas naturales: alguien dejó señales hace mucho tiempo.\n\n"
            "Siguiendo las marcas, encuentras un sendero oculto entre las raíces."
        ),
        "image_url": "https://telegram.org/img/t_logo.png",
        "buttons": [
            {
                "label": "⬅️ Volver",
                "to_room": "arboles",
            },
        ],
    },
}
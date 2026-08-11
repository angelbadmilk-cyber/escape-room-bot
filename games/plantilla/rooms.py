# Plantilla básica para crear un juego nuevo.
#
# Para crear un juego nuevo:
# 1. Copia esta carpeta.
# 2. Cambia el nombre de la carpeta.
# 3. Modifica las habitaciones.
# 4. Registra el juego nuevo en games/registry.py.
# 5. Activa el juego nuevo con "enabled": True.
#
# Esta plantilla incluye ejemplos de:
# - Habitaciones
# - Botones
# - Flags
# - Puzles con código
# - Enlaces externos


START_ROOM = "inicio"


ROOMS = {
    "inicio": {
        "title": "Inicio de la plantilla",
        "text": (
            "Esta es la habitación inicial de la plantilla.\n\n"
            "Puedes copiar este juego de ejemplo para crear una aventura nueva.\n\n"
            "Cada habitación puede tener texto, botones, imágenes, flags y puzles."
        ),
        "buttons": [
            {
                "label": "🚪 Avanzar",
                "to_room": "sala_ejemplo",
            },
            {
                "label": "🔍 Buscar objeto de prueba",
                "callback": "flag:objeto_demo",
                "hide_if_flag": "objeto_demo",
            },
        ],
    },

    "sala_ejemplo": {
        "title": "Sala de ejemplo",
        "text": (
            "Esta es una sala de ejemplo.\n\n"
            "Puedes añadir aquí descripciones, pistas, botones y puzles.\n\n"
            "Si encontraste el objeto de prueba, puedes verlo con /estado."
        ),
        "buttons": [
            {
                "label": "🔗 Enlace de ejemplo",
                "url": "https://example.com",
            },
            {
                "label": "🔑 Introducir código",
                "callback": "code:codigo_demo",
            },
            {
                "label": "⬅️ Volver al inicio",
                "to_room": "inicio",
            },
        ],
        "puzzles": {
            "codigo_demo": {
                "prompt": (
                    "Introduce el código de prueba.\n\n"
                    "Código de prueba: DEMO123"
                ),
                "answers": [
                    "DEMO123",
                ],
                "success_room": "final_plantilla",
                "error_text": (
                    "❌ Ese código no es válido."
                ),
            },
        },
    },

    "final_plantilla": {
        "title": "Final de la plantilla",
        "text": (
            "Has llegado al final de la plantilla.\n\n"
            "Esto solo es un ejemplo.\n"
            "Puedes crear tantas habitaciones como necesites."
        ),
        "buttons": [
            {
                "label": "🔄 Volver al inicio",
                "to_room": "inicio",
            },
        ],
    },
}
# Habitaciones del juego: Castillo Maldito.


START_ROOM = "intro"


ROOMS = {
    "intro": {
        "title": "El susurro del castillo",
        "text": (
            "La tormenta te ha empujado hasta aquí.\n\n"
            "No recuerdas el camino, ni cuántas horas llevas caminando bajo la lluvia. "
            "Solo sabes que, cuando el relámpago iluminó la colina, viste el castillo por primera vez.\n\n"
            "Y algo en ti reconoció el lugar.\n\n"
            "<i>Dicen que nadie entra dos veces al Castillo Maldito.</i>\n"
            "<i>La primera vez, el castillo te observa.</i>\n"
            "<i>La segunda, te reconoce.</i>\n"
            "<i>La tercera... no te deja salir.</i>\n\n"
            "Las puertas se abren solas cuando te acercas, como si te estuvieran esperando.\n\n"
            "Esta noche, el castillo te ha elegido."
        ),
        "image_url": "https://i.ibb.co/PZQ4xSs0/02-intro-susurro.jpg",
        "hint": "Pulsa Entrar al castillo para comenzar.",
        "buttons": [
            {
                "label": "🚪 Entrar al castillo",
                "to_room": "entrada",
            },
        ],
    },

    "entrada": {
        "title": "La entrada del castillo",
        "text": (
            "Cruzas el umbral y las puertas se cierran de golpe detrás de ti.\n\n"
            "El eco resuena por los pasillos como una risa lejana.\n\n"
            "La niebla se arrastra por el suelo, viva, hambrienta. "
            "Frente a ti, el vestíbulo se abre en dos direcciones: "
            "una muralla antigua a la izquierda, y el patio de armas a la derecha.\n\n"
            "Huele a piedra húmeda, a madera podrida y a algo más... "
            "algo viejo que no debería estar vivo.\n\n"
            "A lo lejos, una campana suena una sola vez.\n"
            "No ves ningún campanario.\n\n"
            "<i>Ya no hay vuelta atrás.</i>"
        ),
        "image_url": "https://i.ibb.co/ks895ZH5/03-entrada.jpg",
        "hint": "Explora la muralla antes de entrar.",
        "buttons": [
            {
                "label": "🚪 Empujar la puerta",
                "to_room": "patio",
            },
            {
                "label": "🕯️ Examinar la muralla",
                "to_room": "muralla",
            },
        ],
    },

    "muralla": {
        "title": "La muralla",
        "text": (
            "Te acercas a la muralla interior.\n\n"
            "Las piedras están cubiertas de hiedra negra que parece moverse cuando no la miras directamente. "
            "Al tocar una de ellas, sientes que está tibia, como si el castillo respirara.\n\n"
            "Entre las grietas, hay un símbolo grabado: una corona atravesada por una espina.\n\n"
            "Debajo, alguien escribió con letra temblorosa:\n\n"
            "<i>\"El rey no murió. Fue encerrado.\"</i>\n\n"
            "Y más abajo, con letras aún más pequeñas:\n\n"
            "<i>\"Malachar, su consejero, selló las puertas con sangre. "
            "Que el cielo lo perdone, porque yo no puedo.\"</i>\n\n"
            "Quien escribió esto ya no está. Pero su advertencia permanece."
        ),
        "image_url": "https://i.ibb.co/zVPxTSvN/04-muralla.jpg",
        "hint": "Si tienes la antorcha, prueba a iluminar las piedras.",
        "buttons": [
            {
                "label": "⬅️ Volver a la entrada",
                "to_room": "entrada",
            },
            {
                "label": "🔥 Iluminar las piedras con la antorcha",
                "callback": "diary:get:pagina_reina",
                "requires_flag": "antorcha",
                "hide_if_flag": "pagina_reina",
            },
            {
                "label": "👣 Seguir un ruido extraño",
                "to_room": "patio",
            },
        ],
    },

    "patio": {
        "title": "El patio de armas",
        "text": (
            "Entras en el patio de armas.\n\n"
            "El suelo está cubierto de hojas secas y ceniza, como si hubiera ardido algo hace mucho tiempo. "
            "En el centro, una fuente seca sostiene una figura de piedra sin rostro.\n\n"
            "Alguien le arrancó la cara.\n\n"
            "En la base de la fuente, una inscripción casi borrada:\n\n"
            "<i>\"Aquí yace la reina, sin nombre, sin rostro, sin descanso.\"</i>\n\n"
            "Algo brilla débilmente en el fondo de la fuente seca.\n\n"
            "A la derecha, una torre vigila el patio. "
            "Su puerta de madera está reforzada con hierro oxidado y cerrada con una vieja cerradura.\n\n"
            "A la izquierda, una escalera desciende hacia la oscuridad.\n"
            "<i>La cripta está demasiado oscura para bajar sin luz.</i>"
        ),
        "image_url": "https://i.ibb.co/bSbMtKv/05-patio.jpg",
        "hint": "Busca en la fuente para abrir la torre.",
        "buttons": [
            {
                "label": "⬅️ Volver a la entrada",
                "to_room": "entrada",
            },
            {
                "label": "🔍 Buscar en la fuente",
                "callback": "flag:llave_oxidada",
                "hide_if_flag": "llave_oxidada",
            },
            {
                "label": "🗼 Abrir la puerta de la torre",
                "to_room": "torre",
                "requires_flag": "llave_oxidada",
            },
            {
                "label": "🕯️ Bajar a la cripta",
                "to_room": "cripta",
                "requires_flag": "antorcha",
            },
        ],
    },

    "torre": {
        "title": "La torre",
        "text": (
            "La puerta de la torre chirría al abrirse.\n\n"
            "Dentro hace más frío que fuera. El aire huele a tinta y a secretos.\n\n"
            "Una escalera de caracol sube hacia la oscuridad. "
            "Este era el lugar desde donde el consejero Malachar vigilaba al rey encerrado.\n\n"
            "En el primer escalón hay una antorcha apagada, pero la yesca está seca.\n\n"
            "En la pared, alguien grabó una frase con rabia:\n\n"
            "<i>\"Malachar escondió la verdad en los espejos. "
            "El sello del heredero abrirá la capilla donde descansa la corona.\"</i>\n\n"
            "Y debajo, con letra más serena:\n\n"
            "<i>\"Malachar no sabía que el rey tenía un heredero. Ese es su error.\"</i>"
        ),
        "image_url": "https://i.ibb.co/zWFn9vJW/06-torre.jpg",
        "hint": "Enciende la antorcha.",
        "buttons": [
            {
                "label": "🔥 Encender la antorcha",
                "callback": "flag:antorcha",
                "hide_if_flag": "antorcha",
            },
            {
                "label": "📖 Examinar las notas de Malachar",
                "callback": "diary:get:pagina_malachar",
                "hide_if_flag": "pagina_malachar",
            },
            {
                "label": "⬅️ Volver al patio",
                "to_room": "patio",
            },
        ],
    },

    "cripta": {
        "title": "La cripta",
        "text": (
            "Bajas a la cripta con la antorcha encendida.\n\n"
            "El aire huele a tierra antigua y a metal oxidado. "
            "Las llamas proyectan sombras que se mueven un segundo tarde.\n\n"
            "Hay varios nichos abiertos, como si alguien hubiera removido los cuerpos hace tiempo.\n\n"
            "<i>Tres nichos fueron profanados.</i>\n"
            "<i>Tres almas no descansan.</i>\n"
            "<i>Tres veces su número abrirá la cámara secreta.</i>\n\n"
            "Estos son los sirvientes que murieron encerrados con el rey. "
            "Sus nombres fueron borrados de la historia, pero no de la piedra.\n\n"
            "Sobre una lápida hay una hendidura donde se puede introducir un código."
        ),
        "image_url": "https://i.ibb.co/wFCQ1B2P/07-cripta.jpg",
        "hint": "Lee atentamente el texto. La respuesta está en él.",
        "buttons": [
            {
                "label": "🔑 Introducir código",
                "callback": "code:cripta_codigo",
                "hide_if_flag": "camara_secreta_desbloqueada",
            },
            {
                "label": "🕳️ Entrar a la cámara secreta",
                "to_room": "camara_secreta",
                "requires_flag": "camara_secreta_desbloqueada",
            },
            {
                "label": "⬅️ Volver al patio",
                "to_room": "patio",
            },
        ],
        "puzzles": {
            "cripta_codigo": {
                "prompt": (
                    "Introduce el código que has descubierto en la cripta.\n\n"
                    "<i>Pista: Tres nichos fueron profanados. Tres almas no descansan. "
                    "Tres veces su número abrirá la cámara secreta.</i>"
                ),
                "answers": [
                    "333",
                ],
                "success_flag": "camara_secreta_desbloqueada",
                "success_room": "camara_secreta",
                "error_text": (
                    "❌ <b>El código no es válido.</b>\n\n"
                    "<i>La cripta sigue en silencio.</i>"
                ),
            },
        },
    },

    "camara_secreta": {
        "title": "La cámara secreta",
        "text": (
            "La lápida se mueve lentamente, revelando un pasadizo.\n\n"
            "Detrás aparece una cámara secreta iluminada por una luz verdosa "
            "que no proviene de ninguna fuente visible.\n\n"
            "Las paredes están cubiertas de marcas. Cientos de ellas. Miles.\n\n"
            "Alguien contó los días que pasó encerrado aquí.\n\n"
            "<i>Cuarenta y dos marcas antes de perder la razón.</i>\n"
            "<i>Su último número abrirá el pasadizo.</i>\n\n"
            "Este era el lugar donde encerraron al rey Aldric. "
            "No en una celda, sino en el corazón de su propio castillo.\n\n"
            "Al fondo, un pasadizo estrecho desciende aún más, "
            "pero una losa de piedra bloquea el camino. "
            "Hay una hendidura con forma de número en el centro."
        ),
        "image_url": "https://i.ibb.co/MxWbZBDj/08-camara-secreta.jpg",
        "hint": "Cuenta las marcas del prisionero. Su último número abrirá el pasadizo.",
        "buttons": [
            {
                "label": "🔑 Introducir código",
                "callback": "code:camara_codigo",
                "hide_if_flag": "pasillo_espejos_desbloqueado",
            },
            {
                "label": "📖 Leer las marcas de la pared",
                "callback": "diary:get:pagina_rey",
                "hide_if_flag": "pagina_rey",
            },
            {
                "label": "🕳️ Seguir el pasadizo",
                "to_room": "pasillo_de_los_espejos",
                "requires_flag": "pasillo_espejos_desbloqueado",
            },
            {
                "label": "⬅️ Volver a la cripta",
                "to_room": "cripta",
            },
        ],
        "puzzles": {
            "camara_codigo": {
                "prompt": (
                    "Introduce el número que el prisionero grabó antes de perder la razón.\n\n"
                    "<i>Pista: Cuarenta y dos marcas antes de perder la razón. "
                    "Su último número abrirá el pasadizo.</i>"
                ),
                "answers": [
                    "42",
                ],
                "success_flag": "pasillo_espejos_desbloqueado",
                "success_room": "pasillo_de_los_espejos",
                "error_text": (
                    "❌ <b>La losa no se mueve.</b>\n\n"
                    "<i>El número no es correcto.</i>"
                ),
            },
        },
    },

    "pasillo_de_los_espejos": {
        "title": "El pasillo de los espejos",
        "text": (
            "Entras en un pasillo lleno de espejos rotos.\n\n"
            "En cada fragmento ves tu rostro, pero siempre medio segundo tarde. "
            "Como si los reflejos tuvieran que pensar antes de imitarte.\n\n"
            "Uno de los espejos no refleja la oscuridad: refleja una capilla iluminada por velas. "
            "Pero la capilla no está aquí. No todavía.\n\n"
            "Estos espejos fueron un regalo de Malachar al rey. "
            "Un regalo envenenado: quien se mira en ellos, ve a los que quedaron atrapados.\n\n"
            "Al final del pasillo hay una puerta pequeña con una cruz de hierro.\n"
            "<i>Parece necesitar algún tipo de sello para abrirse.</i>\n\n"
            "Entre los fragmentos de vidrio, algo brilla."
        ),
        "image_url": "https://i.ibb.co/rR4NvPxm/09-pasillo-espejos.jpg",
        "hint": "Busca un sello real entre los espejos.",
        "buttons": [
            {
                "label": "⬅️ Volver a la cámara secreta",
                "to_room": "camara_secreta",
            },
            {
                "label": "👑 Recoger sello real",
                "callback": "flag:sello_real",
                "hide_if_flag": "sello_real",
            },
            {
                "label": "⛪ Entrar en la capilla",
                "to_room": "capilla",
                "requires_flag": "sello_real",
            },
        ],
    },

    "capilla": {
        "title": "La capilla",
        "text": (
            "La capilla está cubierta de polvo blanco, como si hubiera nevado dentro.\n\n"
            "Es el único lugar del castillo que se siente... limpio. Sagrado. "
            "Como si la maldición no pudiera tocarlo del todo.\n\n"
            "En el altar hay una corona rota. "
            "Las velas se encienden solas cuando entras, como si alguien te diera la bienvenida.\n\n"
            "Una voz susurra desde todas partes:\n\n"
            "<i>\"Solo el verdadero heredero puede abrir el salón del trono. "
            "El código del rey está grabado en su corona. "
            "Búscalo donde solo el digno puede verlo.\"</i>\n\n"
            "En la base del altar, casi oculta por el polvo, hay una inscripción:\n\n"
            "<i>\"El miedo es la única prisión de la que no puedes escapar.\"</i>\n\n"
            "El rey Aldric escribió esto antes de morir. Su última enseñanza."
        ),
        "image_url": "https://i.ibb.co/WNrVDRj4/10-capilla.jpg",
        "hint": "Observa la corona para el código. Lee bien las inscripciones.",
        "buttons": [
            {
                "label": "🔗 Abrir puzle web",
                "url": "https://i.ibb.co/jP1j4r2x/1348.jpg",
            },
            {
                "label": "🔑 Introducir código",
                "callback": "code:capilla_codigo",
                "hide_if_flag": "salon_trono_desbloqueado",
            },
            {
                "label": "👑 Tomar la corona rota",
                "callback": "flag:corona",
                "hide_if_flag": "corona",
            },
            {
                "label": "🕯️ Entrar a la cámara de la reina",
                "to_room": "camara_de_la_reina",
                "requires_flags": ["pagina_reina", "pagina_rey", "pagina_malachar"],
            },
            {
                "label": "👑 Entrar al salón del trono",
                "to_room": "salon_trono",
                "requires_flag": "salon_trono_desbloqueado",
            },
            {
                "label": "⬅️ Volver al pasillo",
                "to_room": "pasillo_de_los_espejos",
            },
        ],
        "puzzles": {
            "capilla_codigo": {
                "prompt": (
                    "Introduce el código del rey.\n\n"
                    "<i>Pista: El código está grabado en la corona. "
                    "Pulsa el botón 'Abrir puzle web' para observar la corona de cerca.</i>"
                ),
                "answers": [
                    "1348",
                ],
                "success_flag": "salon_trono_desbloqueado",
                "success_room": "salon_trono",
                "error_text": (
                    "❌ <b>La capilla no acepta ese código.</b>\n\n"
                    "<i>Las velas parpadean con fuerza.</i>"
                ),
            },
        },
    },

    "camara_de_la_reina": {
        "title": "La cámara de la reina",
        "text": (
            "Detrás del altar, una puerta oculta se abre al reconocer las tres páginas del diario.\n\n"
            "Una pequeña cámara bañada por una luz plateada. "
            "En el centro, un espejo de mano que no refleja tu rostro: refleja el de una mujer serena.\n\n"
            "La reina.\n\n"
            "Su voz suena dentro de tu cabeza:\n\n"
            "<i>\"Tres veces me nombraron, pero solo una palabra me devuelve. "
            "Elige la palabra que grabé en mi espejo y recibirás mi bendición.\"</i>"
        ),
        "image_url": "https://i.ibb.co/WNrVDRj4/10-capilla.jpg",
        "hint": "La primera palabra que la reina escribió en su página del diario.",
        "buttons": [
            {
                "label": "🕯️ Miedo",
                "callback": "choice:espejo_reina:MIEDO",
                "hide_if_flag": "bendicion_reina",
            },
            {
                "label": "👑 Corona",
                "callback": "choice:espejo_reina:CORONA",
                "hide_if_flag": "bendicion_reina",
            },
            {
                "label": "💗 Recuerda",
                "callback": "choice:espejo_reina:RECUERDA",
                "hide_if_flag": "bendicion_reina",
            },
            {
                "label": "⬅️ Volver a la capilla",
                "to_room": "capilla",
            },
        ],
        "puzzles": {
            "espejo_reina": {
                "answers": [
                    "RECUERDA",
                ],
                "success_flag": "bendicion_reina",
                "success_text": (
                    "✅ <b>El espejo se enciende.</b>\n\n"
                    "La sonrisa de la reina se dibuja en el cristal.\n\n"
                    "<i>\"Recuerda. Ese fue siempre mi nombre y mi promesa. "
                    "Llévalo contigo, heredero.\"</i>\n\n"
                    "<b>Has recibido la bendición de la reina.</b>"
                ),
                "error_text": (
                    "❌ <b>El espejo permanece frío.</b>\n\n"
                    "<i>Esa no es la palabra que grabé.</i>"
                ),
            },
        },
    },

    "salon_trono": {
        "title": "El salón del trono",
        "text": (
            "Las puertas de la capilla se abren.\n\n"
            "Ante ti aparece el salón del trono. "
            "Está vacío, pero el aire pesa como si hubiera cientos de personas mirándote. "
            "Los sirvientes atrapados. Los que nunca pudieron salir.\n\n"
            "En el trono hay una figura sentada, cubierta por una capa raída.\n\n"
            "<b>El rey Aldric.</b>\n\n"
            "No respira. No se mueve. Murió hace siglos, pero la maldición no le permite descansar.\n\n"
            "Sus ojos vacíos te siguen.\n"
            "Y en su mano huesuda sostiene una llave tallada en hueso.\n\n"
            "De pronto, una voz fría llena la sala:\n\n"
            "<i>\"Responde a mi pregunta, viajero... y la llave será tuya. "
            "Falla... y te quedarás aquí para siempre, como yo.\"</i>\n\n"
            "Detrás del trono hay una puerta enorme, cerrada con un cerrojo de hueso."
        ),
        "image_url": "https://i.ibb.co/kscGLHh6/11-salon-trono.jpg",
        "hint": "El rey te hará una pregunta. Recuerda las inscripciones que has visto.",
        "buttons": [
            {
                "label": "🗝️ Escuchar la pregunta del rey",
                "callback": "code:salon_acertijo",
                "hide_if_flag": "llave_hueso",
            },
            {
                "label": "👑 Escapar con la corona",
                "to_room": "salida_tesoro",
                "requires_flags": ["llave_hueso", "corona"],
            },
            {
                "label": "🚪 Abrir la puerta final",
                "to_room": "salida",
                "requires_flag": "llave_hueso",
            },
            {
                "label": "⭐ Abrazar al rey",
                "to_room": "salida_secreta",
                "requires_flags": ["llave_hueso", "pagina_reina", "pagina_rey", "pagina_malachar"],
            },
            {
                "label": "⬅️ Volver a la capilla",
                "to_room": "capilla",
            },
        ],
        "puzzles": {
            "salon_acertijo": {
                "prompt": (
                    "El rey muerto susurra desde el trono:\n\n"
                    "<i>\"Dime, viajero... ¿qué es lo que nunca podrás escapar de este lugar? "
                    "Lo que te trajo hasta aquí y lo que te seguirá hasta el final. "
                    "Malachar me encerró con cadenas de hierro. "
                    "Pero había una prisión de la que ni él pudo liberarme. "
                    "Recuerda las palabras grabadas en la base del altar de la capilla.\"</i>"
                ),
                "answers": [
                    "MIEDO",
                    "SOMBRA",
                    "MUERTE",
                ],
                "success_flag": "llave_hueso",
                "success_text": (
                    "✅ <b>El rey asiente lentamente.</b>\n\n"
                    "Sus dedos huesudos se abren y dejan caer la llave en tu mano.\n\n"
                    "<i>\"Has respondido bien. Eres digno de salir. "
                    "Yo... por fin puedo descansar.\"</i>\n\n"
                    "<b>Has obtenido la llave de hueso.</b>"
                ),
                "error_text": (
                    "❌ <b>El rey niega con la cabeza.</b>\n\n"
                    "<i>Su susurro se vuelve más frío.</i>\n"
                    "<i>\"Esa no es la respuesta. Piensa en la inscripción del altar.\"</i>"
                ),
            },
        },
    },

    "salida": {
        "title": "El final del castillo",
        "text": (
            "La puerta de hueso se abre lentamente.\n\n"
            "Detrás aparece un pasillo iluminado por la luz del amanecer. "
            "Luz verdadera. Luz del mundo exterior.\n\n"
            "Cruzas el umbral y sientes el sol en la cara por primera vez "
            "en lo que parece una eternidad.\n\n"
            "<b>Has escapado del Castillo Maldito.</b>\n\n"
            "Pero mientras sales, escuchas una última voz a tu espalda. "
            "No es amenazante. Es cansada. Agradecida.\n\n"
            "<i>\"Gracias, viajero. Ahora puedo descansar.\"</i>\n\n"
            "El rey Aldric por fin encuentra la paz que Malachar le negó.\n\n"
            "Si quieres volver a entrar, usa /reiniciar. "
            "Pero ten cuidado: <i>el castillo te recordará.</i>"
        ),
        "image_url": "https://i.ibb.co/76FGGr7/12-salida.jpg",
        "hint": "Has escapado. Puedes usar /reiniciar para jugar de nuevo.",
        "buttons": [
            {
                "label": "🔄 Volver a la entrada",
                "to_room": "entrada",
            },
        ],
    },

    "salida_tesoro": {
        "title": "El final del rey y su tesoro",
        "text": (
            "La puerta de hueso se abre lentamente.\n\n"
            "Cruzas el umbral con la corona rota entre tus manos. "
            "Pesa más de lo que debería, como si cargara con siglos de historia.\n\n"
            "Detrás de ti, la voz del rey Aldric susurra por última vez:\n\n"
            "<i>\"Llévala lejos. Que el mundo recuerde lo que Malachar hizo aquí. "
            "Y que nadie vuelva a cometer mi mismo error: confiar en quien no debe.\"</i>\n\n"
            "<b>Sales al amanecer con el tesoro del rey.</b>\n\n"
            "Has escapado del Castillo Maldito... y te llevas su legado.\n\n"
            "Si quieres probar otro final, usa /reiniciar."
        ),
        "image_url": "https://i.ibb.co/76FGGr7/12-salida.jpg",
        "hint": "Has conseguido el final del tesoro. Prueba /reiniciar para ver el otro final.",
        "buttons": [
            {
                "label": "🔄 Volver a la entrada",
                "to_room": "entrada",
            },
        ],
    },

    "salida_secreta": {
        "title": "El regreso del heredero",
        "text": (
            "No abres la puerta. No tomas la corona.\n\n"
            "Caminas hacia el trono.\n\n"
            "El rey Aldric alza la vista. Sus ojos vacíos se llenan de luz.\n\n"
            "Por primera vez en siglos, sonríe.\n\n"
            "<i>\"Te reconocí en cuanto cruzaste el umbral.\"</i>\n\n"
            "Te arrodillas frente al trono. Las tres páginas que encontraste laten en tu bolsillo, "
            "y de pronto lo recuerdas todo.\n\n"
            "La noche en que Malachar te arrancó de los brazos de tu madre. "
            "Los hechizos que borraron tu nombre. "
            "Los años perdidos en un mundo que no era el tuyo.\n\n"
            "La reina escribió: <i>\"Si lees esto, recuerda.\"</i>\n"
            "El rey escribió: <i>\"Solo un heredero digno puede encontrar la corona.\"</i>\n"
            "Malachar escribió: <i>\"El rey tenía un heredero. Ese es su error.\"</i>\n\n"
            "El error de Malachar. Tu regreso.\n\n"
            "El rey posa su mano huesuda sobre tu cabeza. "
            "La maldición se rompe. El castillo entero tiembla, no con furia, sino con alivio.\n\n"
            "Las puertas se abren de par en par. "
            "Y detrás, en el patio, bajo la luz del amanecer, "
            "hay una mujer esperándote. Sin rostro, pero con los brazos abiertos.\n\n"
            "<b>La reina. Tu madre.</b>\n\n"
            "El castillo no te dejó escapar. Te devolvió a casa.\n\n"
            "<i>Has conseguido el final verdadero.</i>"
        ),
        "image_url": "https://i.ibb.co/76FGGr7/12-salida.jpg",
        "hint": "Has encontrado el final verdadero. Usa /reiniciar para probar los otros finales.",
        "buttons": [
            {
                "label": "🔄 Volver a la entrada",
                "to_room": "entrada",
            },
        ],
    },
}
# Páginas de diario coleccionables del Castillo Maldito.


DIARY_PAGES = {
    "pagina_reina": {
        "title": "📖 Página de la reina",
        "text": (
            "\"Me han robado el rostro y el nombre. Malachar dice que es por el bien "
            "del reino, pero veo la envidia en sus ojos. Aldric no lo ve. Yo sí.\n\n"
            "Si lees esto, recuerda: la reina nunca tuvo miedo.\""
        ),
    },
    "pagina_rey": {
        "title": "📖 Página del rey",
        "text": (
            "\"Día cuarenta y dos. Las fuerzas me abandonan. Malachar cree que ha ganado, "
            "pero olvida que un rey no muere mientras su pueblo lo recuerde.\n\n"
            "He escondido mi corona y mi código donde solo un heredero digno los encuentre.\""
        ),
    },
    "pagina_malachar": {
        "title": "📖 Página de Malachar",
        "text": (
            "\"Que los dioses me perdonen. Sellé las puertas con sangre y ahora el castillo "
            "no me obedece: me reclama. Oigo al rey susurrar en los espejos.\n\n"
            "Ya no salgo de la torre. El castillo me ha convertido en su prisionero, como a él.\""
        ),
    },
}


DIARY_ORDER = ["pagina_reina", "pagina_rey", "pagina_malachar"]


def get_diary_page(flag):
    return DIARY_PAGES.get(flag)


def is_diary_page(flag):
    return flag in DIARY_PAGES


def get_diary_title(flag):
    page = DIARY_PAGES.get(flag)
    if page:
        return page.get("title")
    return flag


def get_diary_text(flag):
    page = DIARY_PAGES.get(flag)
    if page:
        return page.get("text")
    return ""
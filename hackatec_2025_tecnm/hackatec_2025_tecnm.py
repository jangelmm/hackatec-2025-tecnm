# camino_del_maguey/camino_del_maguey.py

import reflex as rx

# Importar las funciones de página para que Reflex las descubra con @rx.page
from .pages.index_page import index
from .pages.registration_page import registration_page
from .pages.lote_viewer_page import lote_viewer_page
from .pages.lotes_list_page import lotes_list_page

# Crear la instancia de la aplicación
# Reflex encontrará automáticamente las páginas decoradas con @rx.page
app = rx.App(
    theme=rx.theme(
        accent_color="amber",
        gray_color="sand",
        radius="medium",
        appearance="light" # Puedes forzar 'light' o 'dark' o dejar 'inherit'
    ),
    # Puedes añadir estilos globales aquí si lo necesitas
    # style={"font_family": "Inter, sans-serif"},
)

# No es necesario llamar a app.add_page() si usas decoradores
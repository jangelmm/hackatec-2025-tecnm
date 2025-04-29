# camino_del_maguey/pages/lotes_list_page.py
import reflex as rx
from ..state import State

@rx.page(route="/lotes", title="Lotes Registrados | Camino del Maguey", on_load=State.load_all_lotes)
def lotes_list_page() -> rx.Component:
     """ Página simple para ver los lotes registrados (útil para debug/navegación). """
     return rx.container(
         rx.vstack(
             rx.heading("Lotes Registrados", size="7"),
             rx.link(rx.button("Registrar Nuevo Lote", variant="outline"), href="/registro", margin_y="1.5em"),
             rx.divider(),
             rx.cond( # Condicional sobre la lista cargada en el estado
                 State.all_lotes_list.length() > 0,
                 rx.vstack(
                     rx.foreach(
                         State.all_lotes_list,
                         lambda lote: rx.card(
                             rx.link(
                                 rx.hstack(
                                     rx.icon(tag="package", size=18, margin_right="0.5em"),
                                     rx.text("Agave: "), 
                                     rx.text(lote['tipo_agave'].to(str), weight="bold"),
                                     rx.spacer(),
                                     rx.badge(lote['id_lote'].to(str).split('-')[0], color_scheme="gray"), 
                                     align="center", width="100%"
                                 ),
                                 href=lote['url_qr_plataforma'].to(str)
                             ),
                             width="100%"
                         )
                     ),
                     spacing="3", # Espacio entre tarjetas
                     width="100%",
                     margin_top="1em"
                 ),
                 # Mensaje si no hay lotes
                 rx.center(rx.text("No hay lotes registrados aún.", color_scheme="gray", margin_top="2em"))
             ),
             align_items="start",
             spacing="3",
             width="100%"
         ),
         max_width="700px",
         padding="2em"
     )
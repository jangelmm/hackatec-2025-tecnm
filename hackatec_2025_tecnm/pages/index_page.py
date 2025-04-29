# camino_del_maguey/pages/index_page.py
import reflex as rx
from ..state import State # Acceder al estado desde el directorio padre

@rx.page(route="/", title="Inicio | Camino del Maguey", on_load=State.initialize_app) # Llama a init en on_load
def index() -> rx.Component:
    """Página de inicio y panel de control simple."""
    return rx.container(
        rx.vstack(
            rx.image(src="assets/logo_placeholder.png", width="100px", height="auto", margin_bottom="1em"), # Añadir un logo si tienes
            rx.heading("Camino del Maguey", size="8"), # Nehza Dohba?
            rx.text("Plataforma de Trazabilidad y Contacto Directo para Mezcal Artesanal", size="5", color_scheme="gray"),
            rx.divider(margin_y="1.5em"),

            rx.hstack(
                rx.button("Registrar Nuevo Lote", on_click=rx.redirect("/registro"), size="3", variant="solid"),
                rx.button("Ver Lotes Registrados", on_click=rx.redirect("/lotes"), size="3", variant="outline"),
                spacing="4",
                margin_bottom="1.5em"
            ),

            # Controles de Simulación Offline y Sincronización
            rx.box(
                rx.hstack(
                    # Botón para Simular Offline (para Demo)
                    rx.button(
                        rx.cond(State.is_offline_mode, "Modo Offline (Activo)", "Modo Online"),
                        rx.icon(tag=rx.cond(State.is_offline_mode, "wifi-off", "wifi"), size=16, margin_left="0.5em"),
                        on_click=State.toggle_offline_mode,
                        color_scheme=rx.cond(State.is_offline_mode, "orange", "grass"),
                        variant="soft",
                        size="2",
                        title="Simular conexión / desconexión"
                    ),
                    # Botón para Sincronizar (condicional)
                    rx.cond(
                        State.has_pending_lotes_var,
                        rx.button(
                            f"Sincronizar ({State.pending_lotes.length()})",
                             rx.icon(tag="cloud_upload", size=16, margin_left="0.5em"),
                            on_click=State.sync_pending_lotes,
                            color_scheme="blue",
                            size="2",
                            is_disabled=State.is_offline_mode # Deshabilitado si está offline
                        ),
                        # Mostrar nada si no hay pendientes
                        rx.fragment("")
                    ),
                    justify="center",
                    spacing="3",
                ),
                padding="1em",
                border="1px dashed var(--gray-a7)",
                border_radius="var(--radius-3)",
                width="100%",
                max_width="500px"
            ),


            # Mensajes de Estado
             rx.cond(
                 State.sync_message,
                 rx.callout.root(
                     rx.callout.icon(rx.icon("info")),
                     rx.callout.text(State.sync_message),
                     margin_top="1em",
                     size="1"
                 )
             ),

             rx.cond(
                 State.has_pending_lotes_var,
                 rx.text(f"{State.pending_lotes.length()} lote(s) pendiente(s) de sincronizar.", size="2", color_scheme="orange", margin_top="1em")
             ),

            spacing="4",
            align="center",
            margin_top="2em",
            min_height="60vh",
            # justify_content="center" # Quitar para que no quede todo al medio si hay poco contenido
        ),
        center_content=True,
        max_width="800px"
    )
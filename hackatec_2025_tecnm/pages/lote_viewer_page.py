# camino_del_maguey/pages/lote_viewer_page.py
import reflex as rx
from typing import Any
from ..state import State

# Helper para mostrar info si existe, o un texto por defecto
def display_info(label: str, value: rx.Var | Any, default_text: str = "No especificado.") -> rx.Component:
    return rx.vstack(
        rx.heading(label, size="4", margin_bottom="0.2em", color_scheme="gray"),
        rx.text(rx.cond(value, value, default_text), size="3"),
        align_items="start",
        spacing="1",
        margin_bottom="1em" # Espacio entre bloques de info
    )

@rx.page(route="/lotes/[lote_id]", title="Detalle del Lote | Camino del Maguey", on_load=State.load_current_lote_on_page_load)
def lote_viewer_page() -> rx.Component:
    """Página pública que muestra la información de un lote específico."""
    return rx.container(
        # --- Evento on_mount para Cargar Datos ---
        # Usamos rx.call_script para asegurar que State.router.page.params esté disponible
        # rx.script(f"console.log('Montando página para lote:', '{State.router.page.params.get('lote_id')}')"), # Debug en consola del navegador
        # rx.box(on_mount=lambda: State.load_lote_data(State.router.page.params.get("lote_id", ""))),

        # --- Manejo de Carga y Errores ---
        rx.cond(
            State.is_loading_lote,
            rx.center(rx.vstack(rx.spinner(size="3"), rx.text("Cargando datos del lote...")), height="60vh")
        ),
        rx.cond(
            State.viewer_error_message & ~State.is_loading_lote,
            rx.center(
                rx.callout.root(
                    rx.callout.icon(rx.icon("circle_alert")),
                    rx.callout.text(State.viewer_error_message),
                    color_scheme="red",
                    size="2"
                ),
                height="60vh"
            )
        ),

        # --- Contenido Principal (si hay datos y no hay error) ---
        rx.cond(
            State.current_lote_data & ~State.is_loading_lote & ~State.viewer_error_message,
            rx.vstack(
                # --- Sección Maestro ---
                rx.card(
                     rx.hstack(
                         # Avatar / Foto Perfil
                         rx.cond(
                             State.current_lote_data["foto_perfil_url"],
                             rx.avatar(fallback="M", src=State.current_lote_data["foto_perfil_url"], size="6", radius="full", high_contrast=True),
                             rx.avatar(fallback=State.current_lote_data["nombre_maestro"].to(str)[0], size="6", radius="full", high_contrast=True)
                         ),
                         # Info Maestro y Contacto
                         rx.vstack(
                             rx.heading(State.current_lote_data["nombre_maestro"], size="6", trim="both"),
                             rx.text("Maestro Mezcalero", size="2", color_scheme="gray"),
                             rx.link(
                                 rx.button(
                                     rx.icon(tag="message-circle", size=18), "Contactar por WhatsApp",
                                     size="2", margin_top="0.5em", color_scheme="green", variant="solid"
                                 ),
                                 href=rx.cond(
                                     State.current_lote_data["whatsapp_maestro"],
                                     f"https://wa.me/{State.current_lote_data['whatsapp_maestro']}",
                                     "#"
                                 ),
                                 is_external=True
                             ),
                             align_items="start", spacing="1"
                         ),
                         spacing="4", align="center"
                     ),
                     # Historia y Audio
                     rx.cond(
                          State.current_lote_data["historia_maestro"],
                          rx.text(State.current_lote_data["historia_maestro"], margin_top="1em", size="3", color_scheme="gray")
                     ),
                     rx.cond(
                         State.current_lote_data["audio_zapoteco_url"],
                         rx.box(
                             rx.text("Escucha al maestro (Zapoteco):", size="2", margin_bottom="0.2em", color_scheme="gray"),
                             rx.audio(url=State.current_lote_data["audio_zapoteco_url"], controls=True), # Añadir controles
                             margin_top="1em"
                         )
                     ),
                     width="100%", variant="surface", margin_bottom="1.5em"
                ),

                # --- Sección Lote ---
                rx.heading(f"Lote: {State.current_lote_data['tipo_agave']}", size="7", margin_bottom="0.5em"),
                rx.text(f"Producción: {State.current_lote_data.get('fecha_produccion', 'No especificada')}", size="3", color_scheme="gray"),
                rx.divider(margin_y="1em"),

                # Grid para detalles / foto / video
                rx.grid(
                    # Columna Izquierda: Detalles Texto
                    rx.vstack(
                        display_info("Notas de Cata", State.current_lote_data.get("notas_cata")),
                        display_info("Proceso de Elaboración", State.current_lote_data.get("descripcion_proceso"), default_text="Proceso artesanal."),
                        align_items="start", width="100%"
                    ),
                    # Columna Derecha: Foto y Video
                    rx.vstack(
                         # Foto Principal
                         rx.cond(
                             State.current_lote_data.get("foto_url"),
                             rx.image(
                                 src=State.current_lote_data["foto_url"],
                                 width="100%", height="auto", fit="contain", max_height="350px",
                                 border_radius="var(--radius-3)", border="1px solid var(--gray-a5)"
                             ),
                             # Placeholder si no hay foto
                             rx.center(rx.vstack(rx.icon(tag="image-off", size=32, color="var(--gray-a9)"), rx.text("Sin foto", color_scheme="gray")), border="1px dashed var(--gray-a7)", height="200px", width="100%", border_radius="var(--radius-3)")
                         ),
                         # Video de YouTube
                         rx.cond(
                            State.youtube_embed_url,
                            rx.box(
                                rx.heading("Video del Proceso", size="4", margin_top="1.5em", margin_bottom="0.5em"),
                                rx.aspect_ratio( # Mantiene proporción 16:9
                                    rx.video(
                                        url=State.youtube_embed_url,
                                        width="100%",
                                        height="100%", # Ocupa todo el aspect ratio
                                        controls=True, # Añadir controles
                                        playing=False, # No auto-play
                                    ),
                                    ratio=16/9
                                ),
                                width="100%", margin_top="1em"
                            )
                        ),
                         align_items="center", width="100%", spacing="4"
                    ),
                    columns="1fr 1fr", # Dos columnas de igual tamaño fraccional
                    spacing="5", width="100%", align_items="start", margin_top="1.5em"
                ),

                # --- Información de Trazabilidad ---
                rx.box(
                     rx.heading("Trazabilidad", size="3", margin_bottom="0.3em", margin_top="2em"),
                     rx.text(f"ID del Lote:", rx.code(State.current_lote_data['id_lote']), size="2"),
                     rx.text(f"URL:", rx.code_block(State.current_lote_data['url_qr_plataforma'], can_copy=True, language="markup"), size="2"),
                     margin_top="2em", padding="1em", border="1px solid var(--gray-a5)", border_radius="var(--radius-2)", width="100%"
                ),

                spacing="4", width="100%", padding_bottom="3em"
            )
        ),

        # Footer simple o link de vuelta
        rx.center(rx.link("Volver al inicio", href="/", margin_top="3em", color_scheme="gray")),

        max_width="1000px", # Ancho máximo
        padding="1.5em" # Padding general
    )
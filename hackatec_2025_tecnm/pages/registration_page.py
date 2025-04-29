# camino_del_maguey/pages/registration_page.py
import reflex as rx
from ..state import State
from typing import Any # Necesario para el lambda de on_change

# --- Componentes UI Reutilizables (sin cambios) ---
def form_input(label: str, name: str, placeholder: str, value: rx.Var, on_change: rx.EventHandler, type: str = "text", required: bool = False) -> rx.Component:
    return rx.form.field(
        rx.vstack(
            rx.hstack(
                rx.form.label(label),
                rx.cond(required, rx.text("*", color_scheme="red")),
                spacing="1"
            ),
            rx.input(
                name=name, placeholder=placeholder, value=value,
                on_change=on_change, type=type, width="100%", required=required
            ),
            align_items="start", width="100%"
        ),
        width="100%", margin_bottom="0.8em"
   )

def form_textarea(label: str, name: str, placeholder: str, value: rx.Var, on_change: rx.EventHandler, rows: int = 3) -> rx.Component:
     return rx.form.field(
         rx.vstack(
             rx.form.label(label),
             rx.text_area(
                 name=name, placeholder=placeholder, value=value,
                 on_change=on_change, width="100%", rows=str(rows)
             ),
             align_items="start", width="100%"
         ),
         width="100%", margin_bottom="0.8em"
     )

@rx.page(route="/registro", title="Registrar Lote | Camino del Maguey")
def registration_page() -> rx.Component:
    """Página para registrar un nuevo lote y los datos del maestro asociado."""
    return rx.container(
         rx.vstack(
            rx.heading("Registrar Nuevo Lote y Maestro", size="7", margin_bottom="1em"),
            rx.form.root(
                 rx.vstack(
                     # --- Sección Maestro Mezcalero --- ### NUEVO ###
                     rx.heading("Datos del Maestro Mezcalero", size="5", margin_bottom="0.5em", margin_top="0.5em"),
                     form_input(
                         "Nombre Completo*", "maestro_nombre", "Nombre y apellidos",
                         State.form_lote_data["maestro_nombre"],
                         lambda v: State.set_form_field("maestro_nombre", v),
                         required=True
                     ),
                     form_input(
                         "WhatsApp*", "maestro_whatsapp", "Ej: 5219511234567 (con código país)",
                         State.form_lote_data["maestro_whatsapp"],
                         lambda v: State.set_form_field("maestro_whatsapp", v),
                         type="tel", required=True
                     ),
                     form_textarea(
                         "Breve Historia (Opcional)", "maestro_historia", "Generaciones, comunidad, etc.",
                         State.form_lote_data["maestro_historia"],
                         lambda v: State.set_form_field("maestro_historia", v),
                         rows=2
                     ),
                      form_input(
                         "URL Google Maps (Opcional)", "maestro_maps_url", "Enlace de Google Maps (https://goo.gl/maps/...)",
                         State.form_lote_data["maestro_maps_url"],
                         lambda v: State.set_form_field("maestro_maps_url", v),
                         type="url"
                     ),
                     rx.divider(margin_y="1.5em"),

                     # --- Sección Datos del Lote ---
                     rx.heading("Datos del Lote", size="5", margin_bottom="0.5em"),
                     form_input("Tipo de Agave*", "tipo_agave", "Ej: Espadín, Tobalá...", State.form_lote_data["tipo_agave"], lambda v: State.set_form_field("tipo_agave", v), required=True),
                     form_input("Fecha Aproximada de Producción", "fecha_produccion", "Ej: 2024-05, Cosecha 2023...", State.form_lote_data["fecha_produccion"], lambda v: State.set_form_field("fecha_produccion", v), type="text"),
                     form_textarea("Notas de Cata", "notas_cata", "Aromas, sabores, sensación...", State.form_lote_data["notas_cata"], lambda v: State.set_form_field("notas_cata", v)),
                     form_textarea("Descripción del Proceso", "descripcion_proceso", "Molienda, fermentación, destilación...", State.form_lote_data["descripcion_proceso"], lambda v: State.set_form_field("descripcion_proceso", v), rows=4),
                     form_input("Enlace Video YouTube (Opcional)", "video_yt_url", "URL completa del video...", State.form_lote_data["video_yt_url"], lambda v: State.set_form_field("video_yt_url", v), type="url"),
                     form_input("Enlace Foto Principal (Opcional)", "foto_url", "URL de una imagen...", State.form_lote_data["foto_url"], lambda v: State.set_form_field("foto_url", v), type="url"),

                     # --- Mensajes de Estado/Error ---
                     rx.cond(
                         State.form_error_message,
                         rx.callout.root(rx.callout.icon(rx.icon("triangle_alert")), rx.callout.text(State.form_error_message), color_scheme="red", margin_y="1em", size="1")
                     ),
                      rx.cond(
                         State.sync_message,
                         rx.callout.root(rx.callout.icon(rx.icon("info")), rx.callout.text(State.sync_message), color_scheme="blue", margin_y="1em", size="1")
                     ),

                     # --- Botón de Envío ---
                     rx.button(
                         rx.cond(State.is_offline_mode, "Guardar Lote Offline", "Guardar Lote y Maestro"),
                         rx.icon(tag="save", margin_left="0.5em"),
                         type="submit",
                         width="100%",
                         size="3",
                         margin_top="1em",
                         # ### MODIFICADO ### Deshabilitar si falta info clave de maestro o lote
                         is_disabled=~(State.form_lote_data["maestro_nombre"] & State.form_lote_data["maestro_whatsapp"] & State.form_lote_data["tipo_agave"])
                     ),
                     spacing="0",
                     width="100%"
                 ),
                 on_submit=State.handle_submit_lote,
                 reset_on_submit=False, # El handler resetea si hay éxito
                 width="100%"
            ),

             # --- Mostrar QR Generado --- (Con condicionales para DeprecationWarnings)
             rx.cond(
                State.generated_qr_code & State.generated_lote_url,
                 rx.center(
                     rx.vstack(
                         rx.heading("¡QR Generado!", size="4", margin_top="1.5em", color_scheme="green"),
                         rx.text("Escanea o haz clic para ver el lote:", size="2"),
                         rx.cond(
                             State.generated_lote_url, # Check para href
                             rx.link(
                                 rx.image(
                                     src=State.generated_qr_code, # Check para src
                                     width="180px", height="180px", margin_y="0.5em",
                                     border="1px solid var(--gray-a7)", padding="5px",
                                     background_color="white",
                                 ),
                                 href=State.generated_lote_url,
                                 is_external=False
                             )
                         ),
                         rx.cond(
                            State.generated_lote_url, # Check para child
                            rx.code_block(State.generated_lote_url, can_copy=True, language="markup")
                         ),
                         align="center", spacing="2", border="1px solid var(--gray-a7)",
                         padding="1.5em", border_radius="var(--radius-3)", margin_top="2em",
                         width="fit-content"
                     ),
                 )
             ),

             # --- Controles Offline/Sync ---
             rx.box(
                 rx.hstack(
                     rx.button(
                         rx.cond(State.is_offline_mode, "Modo Offline (Activo)", "Modo Online"),
                         rx.icon(tag=rx.cond(State.is_offline_mode, "wifi-off", "wifi"), size=16, margin_left="0.5em"),
                         on_click=State.toggle_offline_mode,
                         color_scheme=rx.cond(State.is_offline_mode, "orange", "grass"),
                         variant="soft", size="2"
                     ),
                     rx.cond(
                         State.has_pending_lotes_var,
                         rx.button(
                             f"Sincronizar ({State.pending_lotes.length()})",
                             rx.icon(tag="cloud_upload", size=16, margin_left="0.5em"),
                             on_click=State.sync_pending_lotes,
                             color_scheme="blue", size="2",
                             is_disabled=State.is_offline_mode
                         )
                     ),
                     justify="center", spacing="3",
                 ),
                 margin_top="2em"
            ),

             rx.link("Volver al inicio", href="/", margin_top="2em"),

             width="100%",
             max_width="700px",
             align="center",
             padding_bottom="3em"
         ),
         padding_x="1em",
         center_content=True
    )
# camino_del_maguey/pages/registration_page.py
import reflex as rx
from ..state import State

# --- Componentes UI Reutilizables (Definidos aquí para simplicidad) ---
def form_input(label: str, name: str, placeholder: str, value: rx.Var, on_change: rx.EventHandler, type: str = "text", required: bool = False) -> rx.Component:
    """Componente para un campo de formulario."""
    return rx.form.field(
        rx.vstack(
            rx.hstack(
                rx.form.label(label),
                rx.cond(required, rx.text("*", color_scheme="red")), # Indicador visual
                spacing="1"
            ),
            rx.input(
                name=name, # Importante para accesibilidad y forms
                placeholder=placeholder,
                value=value,
                on_change=on_change,
                type=type,
                width="100%",
                required=required
            ),
            align_items="start",
            width="100%"
        ),
        width="100%",
        margin_bottom="0.8em" # Espacio entre campos
   )

def form_textarea(label: str, name: str, placeholder: str, value: rx.Var, on_change: rx.EventHandler, rows: int = 3) -> rx.Component:
     """ Componente para un área de texto en el formulario. """
     return rx.form.field(
         rx.vstack(
             rx.form.label(label),
             rx.text_area(
                 name=name,
                 placeholder=placeholder,
                 value=value,
                 on_change=on_change,
                 width="100%",
                 rows=str(rows)
             ),
             align_items="start",
             width="100%"
         ),
         width="100%",
         margin_bottom="0.8em" # Espacio entre campos
     )


@rx.page(route="/registro", title="Registrar Lote | Camino del Maguey")
def registration_page() -> rx.Component:
    """Página para que el Maestro Mezcalero registre un nuevo lote."""
    return rx.container(
         rx.vstack(
            rx.heading("Registrar Nuevo Lote de Mezcal", size="7", margin_bottom="1em"),
            rx.cond( # Advertencia si no hay maestro ID
                 ~State.form_lote_data["id_maestro"],
                 rx.callout.root(
                     rx.callout.icon(rx.icon("triangle_alert")),
                     rx.callout.text("Error: No se pudo cargar el ID del maestro. Verifica la base de datos o recarga la página."),
                     color_scheme="red", margin_bottom="1em"
                 )
            ),
            rx.form.root(
                 rx.vstack(
                     # Usar los componentes reutilizables
                     form_input("Tipo de Agave*", "tipo_agave", "Ej: Espadín, Tobalá...", State.form_lote_data["tipo_agave"], lambda v: State.set_form_field("tipo_agave", v), required=True),
                     form_input("Fecha Aproximada de Producción", "fecha_produccion", "Ej: 2024-05, Cosecha 2023...", State.form_lote_data["fecha_produccion"], lambda v: State.set_form_field("fecha_produccion", v), type="text"),
                     form_textarea("Notas de Cata", "notas_cata", "Aromas (humo, tierra, fruta...), sabores (agave cocido, cítrico...), sensación en boca...", State.form_lote_data["notas_cata"], lambda v: State.set_form_field("notas_cata", v)),
                     form_textarea("Descripción del Proceso", "descripcion_proceso", "Detalles de la molienda, fermentación, destilación, maestro a cargo...", State.form_lote_data["descripcion_proceso"], lambda v: State.set_form_field("descripcion_proceso", v), rows=4),
                     form_input("Enlace Video YouTube (Opcional)", "video_yt_url", "URL completa del video (youtube.com/watch?v=...)", State.form_lote_data["video_yt_url"], lambda v: State.set_form_field("video_yt_url", v), type="url"),
                     form_input("Enlace Foto Principal (Opcional)", "foto_url", "URL de una imagen del lote o proceso", State.form_lote_data["foto_url"], lambda v: State.set_form_field("foto_url", v), type="url"),

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
                         rx.cond(State.is_offline_mode, "Guardar Offline", "Guardar y Generar QR"),
                         rx.icon(tag="save", margin_left="0.5em"),
                         type="submit",
                         width="100%",
                         size="3",
                         margin_top="1em",
                         # Deshabilitar si falta el ID del maestro
                         is_disabled=~State.form_lote_data["id_maestro"]
                     ),
                     spacing="0", # Ajustar espaciado si es necesario, margin_bottom en field ayuda
                     width="100%"
                 ),
                 on_submit=State.handle_submit_lote,
                 reset_on_submit=False, # El handler resetea manualmente
                 width="100%"
            ),

             # --- Mostrar QR Generado ---
             rx.cond(
                 State.generated_qr_code,
                 rx.center( # Centrar el bloque del QR
                     rx.vstack(
                         rx.heading("¡QR Generado!", size="4", margin_top="1.5em", color_scheme="green"),
                         rx.text("Escanea o haz clic para ver:", size="2"),
                         rx.link(
                             rx.image(
                                 src=State.generated_qr_code,
                                 width="180px",
                                 height="180px",
                                 margin_y="0.5em",
                                 border="1px solid var(--gray-a7)",
                                 padding="5px", # Pequeño padding interno
                                 background_color="white", # Fondo blanco para el QR
                             ),
                             href=State.generated_lote_url,
                             is_external=False # Navegación interna
                         ),
                         rx.code_block(State.generated_lote_url, can_copy=True, language="text"),
                         align="center",
                         spacing="2",
                         border="1px solid var(--gray-a7)",
                         padding="1.5em",
                         border_radius="var(--radius-3)",
                         margin_top="2em",
                         width="fit-content" # Ajustar ancho al contenido
                     ),
                 )
             ),

             # --- Controles Offline/Sync (Repetidos para conveniencia) ---
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
             max_width="700px", # Ancho máximo del formulario
             align="center",
             padding_bottom="3em"
         ),
         padding_x="1em", # Padding horizontal general
         center_content=True # Centrar el vstack principal
    )
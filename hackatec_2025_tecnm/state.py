# camino_del_maguey/state.py
import reflex as rx
import uuid
import json # Necesario si reactivas LocalStorage
from typing import List, Dict, Any, Optional

# Importar utilidades con rutas relativas correctas
from .utils.db_utils import (
    save_lote,
    get_lote_and_maestro,
    get_all_lotes_simple,
    find_or_create_maestro, # ### MODIFICADO ### Usar nueva función
    PLATFORM_BASE_URL,
    init_db
)
from .utils.qr_utils import generate_qr_code_base64


class State(rx.State):
    """Estado principal de la aplicación."""

    # --- Estado del Formulario de Registro ---
    # ### MODIFICADO ### Añadir campos de maestro al formulario
    form_lote_data: Dict[str, Any] = {
        "maestro_nombre": "", # Nuevo campo
        "maestro_whatsapp": "", # Nuevo campo
        "maestro_historia": "", # Nuevo campo (opcional)
        "maestro_maps_url": "", # Nuevo campo (opcional)
        # "id_maestro": "", # Ya no se guarda aquí directamente
        "tipo_agave": "",
        "notas_cata": "",
        "descripcion_proceso": "",
        "fecha_produccion": "",
        "video_yt_url": "",
        "foto_url": ""
    }
    generated_qr_code: Optional[str] = None
    generated_lote_url: Optional[str] = None

    # --- Estado Offline ---
    LOCAL_STORAGE_KEY = "pending_lotes_camino_v1"
    pending_lotes: List[Dict[str, Any]] = []
    is_offline_mode: bool = False

    # --- Estado del Visor de Lote ---
    current_lote_data: Optional[Dict[str, Any]] = None
    is_loading_lote: bool = False
    viewer_error_message: Optional[str] = None

    # --- Estado General / Debug ---
    all_lotes_list: List[Dict[str, Any]] = []
    form_error_message: Optional[str] = None
    sync_message: Optional[str] = None

    # --- Variables Computadas ---
    @rx.var
    def has_pending_lotes_var(self) -> bool:
        return len(self.pending_lotes) > 0

    @rx.var
    def youtube_embed_url(self) -> Optional[str]:
        if not self.current_lote_data: return None
        url = self.current_lote_data.get("video_yt_url", "")
        if not url: return None
        video_id = None
        try:
            if "v=" in url: video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url: video_id = url.split("youtu.be/")[1].split("?")[0]
        except IndexError: return None
        return f"https://www.youtube.com/embed/{video_id}" if video_id else None

    # --- Event Handlers ---

    def initialize_app(self):
        """Llamado al montar la página inicial para preparar la BD."""
        print("Inicializando base de datos...")
        init_db()
        # Ya no necesitamos cargar maestro por defecto aquí
        # Carga inicial de lotes para la lista (opcional, se carga en la página de lista)
        # self.load_all_lotes()

        # return State.load_pending_from_storage # <-- Comentado temporalmente

    async def load_pending_from_storage(self):
        """Carga los lotes pendientes desde LocalStorage."""
        # NECESITA REFACTORIZACIÓN PARA USAR rx.LocalStorage
        print(f"Intentando cargar pendientes - FUNCIONALIDAD DESACTIVADA")
        self.pending_lotes = []

    def set_form_field(self, field: str, value: Any):
        """Actualiza un campo del diccionario del formulario."""
        self.form_lote_data[field] = value
        self.generated_qr_code = None
        self.generated_lote_url = None
        self.form_error_message = None
        self.sync_message = None

    def _validate_form(self) -> bool:
         """ Valida los campos obligatorios del formulario. """
         self.form_error_message = None
         # ### MODIFICADO ### Validar campos de Maestro y Lote
         if not self.form_lote_data.get("maestro_nombre", "").strip():
              self.form_error_message = "El nombre del Maestro Mezcalero es obligatorio."
              return False
         if not self.form_lote_data.get("maestro_whatsapp", "").strip():
              self.form_error_message = "El WhatsApp del Maestro Mezcalero es obligatorio."
              return False
         # Validar formato WhatsApp (simple)? Podría ser más complejo
         # telefono = self.form_lote_data["maestro_whatsapp"].replace("+", "").replace(" ", "")
         # if not telefono.isdigit() or len(telefono) < 10:
         #     self.form_error_message = "El formato del WhatsApp no parece válido."
         #     return False
         if not self.form_lote_data.get("tipo_agave", "").strip():
             self.form_error_message = "El tipo de agave es obligatorio."
             return False
         return True

    async def handle_submit_lote(self):
        """Maneja el envío del formulario de lote."""
        self.generated_qr_code = None
        self.generated_lote_url = None
        self.form_error_message = None
        self.sync_message = None

        if not self._validate_form():
             return

        # ### NUEVO ### Encontrar o crear el maestro ANTES de guardar el lote
        maestro_nombre = self.form_lote_data.get("maestro_nombre")
        maestro_whatsapp = self.form_lote_data.get("maestro_whatsapp")
        maestro_historia = self.form_lote_data.get("maestro_historia", "")
        maestro_maps_url = self.form_lote_data.get("maestro_maps_url", "")

        # Llamada síncrona a la función de BD (Reflex lo maneja en background thread)
        maestro_id = find_or_create_maestro(
            nombre=maestro_nombre,
            whatsapp=maestro_whatsapp,
            historia=maestro_historia,
            maps_url=maestro_maps_url
        )

        if not maestro_id:
             self.form_error_message = "Error al buscar o crear el registro del Maestro Mezcalero."
             print("Error: find_or_create_maestro devolvió None.")
             return

        # Preparar datos del lote incluyendo el ID del maestro obtenido
        lote_data_to_save = self.form_lote_data.copy()
        lote_data_to_save["id_maestro"] = maestro_id # <-- Asociar ID encontrado/creado
        lote_data_to_save["temp_id"] = str(uuid.uuid4()) # ID temporal para offline

        # --- Lógica Offline/Online ---
        if self.is_offline_mode:
            print("Modo Offline: Guardando lote localmente... (FUNCIONALIDAD DESACTIVADA)")
            self.pending_lotes.append(lote_data_to_save)
            # await self.set_local_storage(...) # <-- Comentado
            self.sync_message = f"Lote '{lote_data_to_save['tipo_agave']}' guardado offline (simulado)."
            self._reset_form()
        else:
            print(f"Modo Online: Guardando lote para maestro ID: {maestro_id}...")
            id_lote_nuevo = save_lote(lote_data_to_save) # save_lote ahora usa el id_maestro pasado
            if id_lote_nuevo:
                print(f"Lote guardado en BD con ID: {id_lote_nuevo}")
                lote_url = f"{PLATFORM_BASE_URL}/lotes/{id_lote_nuevo}"
                self.generated_lote_url = lote_url
                self.generated_qr_code = generate_qr_code_base64(lote_url)
                if not self.generated_qr_code:
                     self.form_error_message = "Lote guardado, pero hubo un error al generar QR."
                else:
                     self.sync_message = f"Lote '{lote_data_to_save['tipo_agave']}' para '{maestro_nombre}' guardado y QR generado."
                self._reset_form()
                self.load_all_lotes() # Actualizar lista general
            else:
                self.form_error_message = "Error: No se pudo guardar el lote en la base de datos."

    async def sync_pending_lotes(self):
        """Intenta sincronizar los lotes guardados localmente."""
        # NECESITA REFACTORIZACIÓN PARA USAR rx.LocalStorage
        print("Sincronización pendiente - FUNCIONALIDAD DESACTIVADA")
        self.sync_message = "Funcionalidad de sincronización no implementada."


    def _reset_form(self):
        """ Resetea el diccionario del formulario a valores iniciales. """
        # ### MODIFICADO ### Limpiar todos los campos
        self.form_lote_data = {
            "maestro_nombre": "",
            "maestro_whatsapp": "",
            "maestro_historia": "",
            "maestro_maps_url": "",
            "tipo_agave": "",
            "notas_cata": "",
            "descripcion_proceso": "",
            "fecha_produccion": "",
            "video_yt_url": "",
            "foto_url": ""
        }
        # Limpiar también QR y mensajes
        self.generated_qr_code = None
        self.generated_lote_url = None
        self.form_error_message = None
        # self.sync_message = None # Quizás dejar el último mensaje de sync

    def toggle_offline_mode(self):
        """Cambia el estado de simulación offline."""
        self.is_offline_mode = not self.is_offline_mode
        mode = 'Activado' if self.is_offline_mode else 'Desactivado'
        self.sync_message = f"Modo Offline {mode}."
        print(f"Modo Offline cambiado a: {self.is_offline_mode}")


    def load_lote_data(self, lote_id: Optional[str]):
        """Carga los datos de un lote específico para visualización."""
        self.current_lote_data = None
        self.viewer_error_message = None
        self.is_loading_lote = False

        if not lote_id:
            self.viewer_error_message = "ID de lote inválido o no proporcionado en la URL."
            # print("Error: ID de lote vacío en load_lote_data") # Limpiar consola
            return

        self.is_loading_lote = True
        print(f"Visor: Cargando datos para lote ID: {lote_id}")

        try:
             data = get_lote_and_maestro(lote_id) # Ya incluye Maps_url si existe
             self.is_loading_lote = False

             if data:
                 self.current_lote_data = data
                 print(f"Visor: Datos cargados para {lote_id}")
             else:
                 self.viewer_error_message = f"No se encontró información para el lote con ID: {lote_id}"
                 print(f"Visor: No se encontró lote {lote_id}")
        except Exception as e:
             print(f"Visor: Excepción al cargar lote {lote_id}: {e}")
             self.viewer_error_message = "Ocurrió un error al cargar los datos del lote."
             self.is_loading_lote = False


    def load_all_lotes(self):
        """Carga la lista simple de todos los lotes."""
        print("Cargando lista de todos los lotes...")
        self.all_lotes_list = get_all_lotes_simple()
        print(f"Encontrados {len(self.all_lotes_list)} lotes.")

    def load_current_lote_on_page_load(self):
        """Manejador para on_load de la página de visor de lote."""
        lote_id = self.router.page.params.get("lote_id", "")
        print(f"on_load: Intentando cargar datos para lote_id: '{lote_id}'")
        self.load_lote_data(lote_id)
# camino_del_maguey/state.py
import reflex as rx
import uuid
from typing import List, Dict, Any, Optional

# Importar utilidades con rutas relativas correctas
from .utils.db_utils import (
    save_lote,
    get_lote_and_maestro,
    get_all_lotes_simple,
    get_default_maestro_id,
    PLATFORM_BASE_URL,
    init_db # Importar función de inicialización
)
from .utils.qr_utils import generate_qr_code_base64

# Llamar a init_db aquí asegura que se ejecute una vez al cargar el estado
# init_db() # Comentado: puede causar problemas si el estado se recarga. Mejor llamar en on_load de página inicial.


class State(rx.State):
    """Estado principal de la aplicación Camino del Maguey."""

    # --- Estado del Formulario de Registro ---
    form_lote_data: Dict[str, Any] = {
        "id_maestro": "",
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
    # Nombre único para LocalStorage
    LOCAL_STORAGE_KEY = "pending_lotes_camino_v1"
    pending_lotes: List[Dict[str, Any]] = []
    is_offline_mode: bool = False # Simulador

    # --- Estado del Visor de Lote ---
    current_lote_data: Optional[Dict[str, Any]] = None
    is_loading_lote: bool = False
    viewer_error_message: Optional[str] = None # Error específico del visor

    # --- Estado General / Debug ---
    all_lotes_list: List[Dict[str, Any]] = []
    form_error_message: Optional[str] = None # Error específico del formulario
    sync_message: Optional[str] = None # Mensaje de estado de sincronización

    # --- Variables Computadas ---
    @rx.var
    def has_pending_lotes_var(self) -> bool:
        """Indica si hay lotes pendientes en el estado."""
        return len(self.pending_lotes) > 0

    @rx.var
    def youtube_embed_url(self) -> Optional[str]:
        """Genera la URL de embed para un video de YouTube."""
        if not self.current_lote_data:
            return None
        url = self.current_lote_data.get("video_yt_url", "")
        if not url:
            return None

        video_id = None
        try:
            # Intentar extraer ID de URLs comunes
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            # Añadir más patrones si es necesario
        except IndexError:
            print(f"No se pudo extraer video_id de: {url}")
            return None # URL inválida o no soportada

        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None

    # --- Event Handlers ---

    # Inicialización
    # state.py - dentro de la clase State
    def initialize_app(self):
        """Llamado al montar la página inicial para preparar la BD y cargar pendientes."""
        print("Inicializando base de datos...")
        init_db() # Asegura que la BD y tablas existan

        # Obtener ID *después* de init_db y asignar al estado del form
        maestro_id = get_default_maestro_id()
        self.form_lote_data["id_maestro"] = maestro_id or ""
        print(f"Maestro ID por defecto asignado al formulario: {self.form_lote_data['id_maestro']}")

        # Ya no necesitas modificar el global DEFAULT_MAESTRO_ID aquí
        # global DEFAULT_MAESTRO_ID # <-- Eliminar
        # DEFAULT_MAESTRO_ID = get_default_maestro_id() # <-- Eliminar

        # Cargar pendientes desde LocalStorage (async)
        return State.load_pending_from_storage

    async def load_pending_from_storage(self):
        """Carga los lotes pendientes desde LocalStorage."""
        print(f"Intentando cargar pendientes desde LocalStorage (Key: {self.LOCAL_STORAGE_KEY})")
        stored_pending = await self.get_local_storage(self.LOCAL_STORAGE_KEY)
        if isinstance(stored_pending, list):
            self.pending_lotes = stored_pending
            print(f"Cargados {len(self.pending_lotes)} lotes pendientes.")
        else:
            self.pending_lotes = []
            if stored_pending is not None:
                 print(f"Advertencia: Datos inválidos encontrados en LocalStorage para {self.LOCAL_STORAGE_KEY}. Se reseteó a lista vacía.")
            else:
                 print("No se encontraron lotes pendientes en LocalStorage.")


    # Formulario y Sincronización
    def set_form_field(self, field: str, value: Any):
        """Actualiza un campo del diccionario del formulario."""
        self.form_lote_data[field] = value
        # Limpiar mensajes/QR al modificar
        self.generated_qr_code = None
        self.generated_lote_url = None
        self.form_error_message = None
        self.sync_message = None

    def _validate_form(self) -> bool:
         """ Valida los campos obligatorios del formulario. """
         self.form_error_message = None
         if not self.form_lote_data.get("id_maestro"):
              self.form_error_message = "Error interno: Falta ID del Maestro. Recarga la página."
              print("Error Crítico: Falta DEFAULT_MAESTRO_ID")
              return False
         if not self.form_lote_data.get("tipo_agave", "").strip():
             self.form_error_message = "El tipo de agave es obligatorio."
             return False
         # Añadir más validaciones si es necesario (ej. formato URL)
         return True

    async def handle_submit_lote(self):
        """Maneja el envío del formulario de lote."""
        # Limpiar estado previo
        self.generated_qr_code = None
        self.generated_lote_url = None
        self.form_error_message = None
        self.sync_message = None

        if not self._validate_form():
             return # Detener si la validación falla

        lote_data_to_save = self.form_lote_data.copy()
        lote_data_to_save["temp_id"] = str(uuid.uuid4()) # ID temporal para offline

        if self.is_offline_mode:
            # --- Guardado Offline ---
            print("Modo Offline: Guardando lote localmente...")
            self.pending_lotes.append(lote_data_to_save) # Añadir a la lista en memoria
            await self.set_local_storage(self.LOCAL_STORAGE_KEY, self.pending_lotes) # Actualizar LocalStorage
            print(f"Lote añadido a pendientes. Total: {len(self.pending_lotes)}")
            self.sync_message = f"Lote '{lote_data_to_save['tipo_agave']}' guardado offline. {len(self.pending_lotes)} pendiente(s)."
            # Resetear formulario
            self._reset_form()
        else:
            # --- Guardado Online ---
            print("Modo Online: Guardando lote en backend...")
            id_lote_nuevo = save_lote(lote_data_to_save)
            if id_lote_nuevo:
                print(f"Lote guardado en BD con ID: {id_lote_nuevo}")
                lote_url = f"{PLATFORM_BASE_URL}/lotes/{id_lote_nuevo}"
                self.generated_lote_url = lote_url
                self.generated_qr_code = generate_qr_code_base64(lote_url)
                if not self.generated_qr_code:
                     self.form_error_message = "Lote guardado, pero hubo un error al generar el código QR."
                else:
                     self.sync_message = f"Lote '{lote_data_to_save['tipo_agave']}' guardado y QR generado."
                self._reset_form()
                self.load_all_lotes() # Actualizar lista de lotes visibles
            else:
                self.form_error_message = "Error: No se pudo guardar el lote en la base de datos."
                print("Error en save_lote desde el backend.")

    async def sync_pending_lotes(self):
        """Intenta sincronizar los lotes guardados localmente."""
        if self.is_offline_mode:
            self.sync_message = "No se puede sincronizar en modo offline."
            print("Intento de sincronización en modo offline bloqueado.")
            return

        if not self.pending_lotes:
            self.sync_message = "No hay lotes pendientes para sincronizar."
            print("No hay lotes pendientes.")
            return

        print(f"Iniciando sincronización de {len(self.pending_lotes)} lotes pendientes...")
        self.sync_message = f"Sincronizando {len(self.pending_lotes)} lote(s)..."

        remaining_pending = [] # Lotes que fallaron la sincronización
        succeeded_count = 0

        # Iterar sobre una copia para poder modificar self.pending_lotes si es necesario
        lotes_a_sincronizar = list(self.pending_lotes)
        self.pending_lotes = [] # Limpiar estado local temporalmente

        for lote_pendiente in lotes_a_sincronizar:
            id_lote_nuevo = save_lote(lote_pendiente)
            if id_lote_nuevo:
                succeeded_count += 1
                print(f"Lote pendiente {lote_pendiente.get('temp_id')} sincronizado con ID: {id_lote_nuevo}")
                # Opcional: Generar QR aquí si se quiere mostrar algo post-sync
            else:
                print(f"Fallo al sincronizar lote pendiente: {lote_pendiente.get('temp_id')}")
                remaining_pending.append(lote_pendiente) # Añadir a la lista de fallidos

        self.pending_lotes = remaining_pending # Actualizar estado con los fallidos
        await self.set_local_storage(self.LOCAL_STORAGE_KEY, self.pending_lotes) # Guardar restantes

        result_message = f"Sincronización: {succeeded_count} éxito(s), {len(remaining_pending)} fallo(s)."
        self.sync_message = result_message
        print(result_message)
        if succeeded_count > 0:
            self.load_all_lotes() # Actualizar lista general si hubo cambios

    # state.py - dentro de la clase State
    def _reset_form(self):
        """ Resetea el diccionario del formulario a valores iniciales. """
        maestro_id = get_default_maestro_id() # Re-obtener por si acaso
        self.form_lote_data = {
            "id_maestro": maestro_id or "",
            "tipo_agave": "",
            "notas_cata": "",
            "descripcion_proceso": "",
            "fecha_produccion": "",
            "video_yt_url": "",
            "foto_url": ""
        }

    def toggle_offline_mode(self):
        """Cambia el estado de simulación offline."""
        self.is_offline_mode = not self.is_offline_mode
        self.sync_message = f"Modo Offline {'Activado' if self.is_offline_mode else 'Desactivado'}."
        print(f"Modo Offline cambiado a: {self.is_offline_mode}")


    # Visor de Lote
    def load_lote_data(self, lote_id: Optional[str]):
        """Carga los datos de un lote específico para visualización."""
        # Resetear estado del visor
        self.current_lote_data = None
        self.viewer_error_message = None
        self.is_loading_lote = False

        if not lote_id:
            self.viewer_error_message = "ID de lote inválido o no proporcionado en la URL."
            print("Error: ID de lote vacío en load_lote_data")
            return

        self.is_loading_lote = True
        print(f"Visor: Cargando datos para lote ID: {lote_id}")
        # yield # Permitir que el UI muestre el spinner

        try:
             data = get_lote_and_maestro(lote_id) # Llamada síncrona a la BD
             self.is_loading_lote = False # Marcar carga como finalizada

             if data:
                 self.current_lote_data = data
                 print(f"Visor: Datos cargados para {lote_id}")
             else:
                 self.viewer_error_message = f"No se encontró información para el lote con ID: {lote_id}"
                 print(f"Visor: No se encontró lote {lote_id}")
        except Exception as e:
             # Capturar cualquier error inesperado durante la carga
             print(f"Visor: Excepción al cargar lote {lote_id}: {e}")
             self.viewer_error_message = "Ocurrió un error al cargar los datos del lote."
             self.is_loading_lote = False


    # Lista General de Lotes
    def load_all_lotes(self):
        """Carga la lista simple de todos los lotes."""
        print("Cargando lista de todos los lotes...")
        self.all_lotes_list = get_all_lotes_simple()
        print(f"Encontrados {len(self.all_lotes_list)} lotes.")

    def load_current_lote_on_page_load(self):
        """Manejador para on_load de la página de visor de lote."""
        # Accede al router desde self
        lote_id = self.router.page.params.get("lote_id", "")
        print(f"on_load: Intentando cargar datos para lote_id: '{lote_id}'") # Log para verificar
        # Llama a la función que ya tenías
        self.load_lote_data(lote_id)
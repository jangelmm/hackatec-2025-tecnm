# Estructura del proyecto


```
/home/angel/Documents/Programacion/Python/Envioroments/hackatec-2025-tecnm
├── assets
│   └── favicon.ico
├── hackatec_2025_tecnm
│   ├── pages
│   │   ├── __init__.py
│   │   ├── index_page.py
│   │   ├── lote_viewer_page.py
│   │   ├── lotes_list_page.py
│   │   └── registration_page.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── db_utils.py
│   │   └── qr_utils.py
│   ├── __init__.py
│   ├── hackatec_2025_tecnm.py
│   └── state.py
├── README.md
├── generate_markdown.py
├── project_overview.md
├── requirements.txt
└── rxconfig.py
```

## `generate_markdown.py`

```python
import os
import argparse

# Directorios a ignorar (incluye caches de Python)
IGNORE_DIRS = {'.web', 'venv', '__pycache__'}
# Extensiones de archivo permitidas
ALLOWED_EXTS = {'.py', '.java', '.cpp', '.c'}

# Prefijos para el tree
TREE_PREFIXES = {
    'branch': '├── ',
    'last':   '└── ',
    'indent': '    ',
    'pipe':   '│   '
}


def build_tree(root_path):
    """
    Genera una lista de líneas representando la estructura de directorios,
    ignorando IGNORE_DIRS y archivos ocultos.
    """
    tree_lines = []

    def _tree(dir_path, prefix=''):
        entries = [e for e in sorted(os.listdir(dir_path))
                   if not (e in IGNORE_DIRS or e.startswith('.'))]
        dirs = [e for e in entries if os.path.isdir(os.path.join(dir_path, e))]
        files = [e for e in entries if os.path.isfile(os.path.join(dir_path, e))]
        total = len(dirs) + len(files)
        for idx, name in enumerate(dirs + files):
            path = os.path.join(dir_path, name)
            connector = TREE_PREFIXES['last'] if idx == total - 1 else TREE_PREFIXES['branch']
            tree_lines.append(f"{prefix}{connector}{name}")
            if os.path.isdir(path):
                extension = TREE_PREFIXES['indent'] if idx == total - 1 else TREE_PREFIXES['pipe']
                _tree(path, prefix + extension)

    # Línea raíz
    tree_lines.append(root_path)
    _tree(root_path)
    return tree_lines


def collect_files(root_path):
    """
    Recorre recursivamente el directorio y devuelve rutas de archivos
    con extensiones permitidas, omitiendo IGNORE_DIRS.
    """
    paths = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Excluir carpetas no deseadas
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith('.')]
        for fname in sorted(filenames):
            ext = os.path.splitext(fname)[1]
            if ext in ALLOWED_EXTS:
                paths.append(os.path.join(dirpath, fname))
    return paths


def ext_to_lang(ext):
    """Mapea extensión de archivo a lenguaje para Markdown."""
    return {
        '.py': 'python',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c'
    }.get(ext, '')


def main():
    parser = argparse.ArgumentParser(
        description="Genera un Markdown con la estructura tipo tree y el código fuente.")
    parser.add_argument(
        'output', nargs='?', default='project_overview.md',
        help='Nombre del archivo Markdown de salida. (default: project_overview.md)')
    args = parser.parse_args()

    root = os.getcwd()
    tree_lines = build_tree(root)
    code_files = collect_files(root)

    with open(args.output, 'w', encoding='utf-8') as md:
        # Encabezado
        md.write(f"# Estructura del proyecto\n\n")
        # Bloque tree con salto de línea tras ```
        md.write("\n```\n")
        md.write("\n".join(tree_lines))
        md.write("\n```\n\n")

        # Incluir cada archivo y su contenido
        for path in code_files:
            rel_path = os.path.relpath(path, root)
            ext = os.path.splitext(path)[1]
            lang = ext_to_lang(ext)
            md.write(f"## `{rel_path}`\n\n")
            md.write(f"```{lang}\n")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    md.write(f.read())
            except Exception as e:
                md.write(f"# Error al leer el archivo: {e}\n")
            md.write("```\n\n")

    print(f"Archivo Markdown generado: {args.output}")

if __name__ == '__main__':
    main()```

## `rxconfig.py`

```python
import reflex as rx

config = rx.Config(
    app_name="hackatec_2025_tecnm",
)```

## `hackatec_2025_tecnm/__init__.py`

```python
```

## `hackatec_2025_tecnm/hackatec_2025_tecnm.py`

```python
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

# No es necesario llamar a app.add_page() si usas decoradores```

## `hackatec_2025_tecnm/state.py`

```python
# camino_del_maguey/state.py
import reflex as rx
import uuid
from typing import List, Dict, Any, Optional

# Importar utilidades con rutas relativas correctas
from .utils.db_utils import (
    save_lote,
    get_lote_and_maestro,
    get_all_lotes_simple,
    DEFAULT_MAESTRO_ID,
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
        "id_maestro": DEFAULT_MAESTRO_ID or "",
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
    def initialize_app(self):
        """Llamado al montar la página inicial para preparar la BD y cargar pendientes."""
        print("Inicializando base de datos...")
        init_db() # Asegura que la BD y tablas existan
        # Actualizar ID maestro por si se creó en init_db
        global DEFAULT_MAESTRO_ID
        DEFAULT_MAESTRO_ID = get_default_maestro_id()
        self.form_lote_data["id_maestro"] = DEFAULT_MAESTRO_ID or ""
        print(f"Maestro ID por defecto: {self.form_lote_data['id_maestro']}")
        # Cargar pendientes desde LocalStorage (async)
        return State.load_pending_from_storage # Devolver la corutina para que se ejecute

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

    def _reset_form(self):
         """ Resetea el diccionario del formulario a valores iniciales. """
         self.form_lote_data = {
             "id_maestro": DEFAULT_MAESTRO_ID or "",
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
        print(f"Encontrados {len(self.all_lotes_list)} lotes.")```

## `hackatec_2025_tecnm/utils/__init__.py`

```python
```

## `hackatec_2025_tecnm/utils/db_utils.py`

```python
# camino_del_maguey/utils/db_utils.py
import sqlite3
import uuid
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

# Carga variables desde .env ubicado en la raíz del proyecto
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

DB_NAME = "camino_del_maguey.db" # Se creará en la raíz del proyecto
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', DB_NAME)
PLATFORM_BASE_URL = os.getenv("PLATFORM_BASE_URL", "http://localhost:3000") # Valor por defecto

def get_db_connection():
    """Crea y retorna una conexión a la base de datos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # Devuelve filas como diccionarios
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la BD en {DB_PATH}: {e}")
        raise # Relanzar excepción para indicar fallo

def init_db():
    """Inicializa la base de datos creando las tablas si no existen."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Tabla simple para Maestros (asumimos uno o pocos para MVP)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maestros (
                id_maestro TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                historia TEXT,
                whatsapp TEXT NOT NULL,
                audio_zapoteco_url TEXT, -- Placeholder
                foto_perfil_url TEXT  -- Placeholder
            )
        """)

        # Tabla para Lotes de Mezcal
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lotes (
                id_lote TEXT PRIMARY KEY,
                id_maestro TEXT NOT NULL,
                tipo_agave TEXT NOT NULL,
                notas_cata TEXT,
                descripcion_proceso TEXT,
                fecha_produccion TEXT, -- Simplificado como texto
                video_yt_url TEXT,
                foto_url TEXT, -- Simplificado a una URL de foto
                url_qr_plataforma TEXT,
                FOREIGN KEY (id_maestro) REFERENCES maestros (id_maestro)
            )
        """)
        conn.commit()
        conn.close()
        print(f"Base de datos inicializada/verificada en: {DB_PATH}")

        # --- Insertar Maestro de Ejemplo (Solo si la tabla está vacía) ---
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM maestros")
        if cursor.fetchone()[0] == 0:
            maestro_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO maestros (id_maestro, nombre, historia, whatsapp, audio_zapoteco_url, foto_perfil_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                maestro_id,
                "Maestro Ejemplo Chichicapam",
                "Una historia breve sobre generaciones familiares dedicadas al arte del mezcal en San Baltazar Chichicapam.",
                "5219511234567", # Reemplaza con un número real (con código de país + 1)
                # "https://example.com/audio/saludo.mp3", # URL de ejemplo audio
                None, # Sin audio por ahora
                # "https://via.placeholder.com/150/F0A84C/FFFFFF?Text=Maestro", # URL de ejemplo foto
                None, # Sin foto por ahora
            ))
            conn.commit()
            print(f"Maestro de ejemplo insertado con ID: {maestro_id}")
        conn.close()

    except sqlite3.Error as e:
        print(f"Error durante la inicialización de la BD: {e}")
    except Exception as ex:
         print(f"Error inesperado en init_db: {ex}")

def save_lote(lote_data: Dict[str, Any]) -> Optional[str]:
    """Guarda un nuevo lote en la BD y retorna su ID o None si falla."""
    id_lote = str(uuid.uuid4())
    url_qr = f"{PLATFORM_BASE_URL}/lotes/{id_lote}"

    conn = None # Inicializar conn a None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lotes (
                id_lote, id_maestro, tipo_agave, notas_cata,
                descripcion_proceso, fecha_produccion, video_yt_url,
                foto_url, url_qr_plataforma
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_lote,
            lote_data.get("id_maestro"), # El ID debe venir en lote_data
            lote_data.get("tipo_agave", "Agave Desconocido"),
            lote_data.get("notas_cata", ""),
            lote_data.get("descripcion_proceso", ""),
            lote_data.get("fecha_produccion", ""),
            lote_data.get("video_yt_url", ""),
            lote_data.get("foto_url", ""),
            url_qr
        ))
        conn.commit()
        print(f"Lote guardado con ID: {id_lote}")
        return id_lote
    except sqlite3.Error as e:
        print(f"Error SQLite al guardar lote: {e}")
        if conn:
            conn.rollback()
        return None
    except Exception as ex:
         print(f"Error inesperado en save_lote: {ex}")
         if conn:
             conn.rollback()
         return None
    finally:
        if conn:
            conn.close()


def get_lote_and_maestro(id_lote: str) -> Optional[Dict[str, Any]]:
    """Obtiene los datos del lote y su maestro asociado."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                l.id_lote, l.tipo_agave, l.notas_cata, l.descripcion_proceso,
                l.fecha_produccion, l.video_yt_url, l.foto_url, l.url_qr_plataforma,
                m.id_maestro, m.nombre AS nombre_maestro, m.historia AS historia_maestro,
                m.whatsapp AS whatsapp_maestro, m.audio_zapoteco_url, m.foto_perfil_url
            FROM lotes l
            JOIN maestros m ON l.id_maestro = m.id_maestro
            WHERE l.id_lote = ?
        """, (id_lote,))
        result = cursor.fetchone()
        return dict(result) if result else None
    except sqlite3.Error as e:
        print(f"Error SQLite al obtener lote y maestro: {e}")
        return None
    except Exception as ex:
         print(f"Error inesperado en get_lote_and_maestro: {ex}")
         return None
    finally:
        if conn:
            conn.close()

def get_all_lotes_simple() -> List[Dict[str, Any]]:
     """ Obtiene una lista simple de todos los lotes para debug/vista general. """
     conn = None
     try:
         conn = get_db_connection()
         cursor = conn.cursor()
         # Ordenar por fecha si se guarda consistentemente, o por ID
         cursor.execute("SELECT id_lote, tipo_agave, url_qr_plataforma FROM lotes ORDER BY id_lote DESC")
         lotes = [dict(row) for row in cursor.fetchall()]
         return lotes
     except sqlite3.Error as e:
         print(f"Error SQLite al obtener todos los lotes: {e}")
         return []
     except Exception as ex:
          print(f"Error inesperado en get_all_lotes_simple: {ex}")
          return []
     finally:
        if conn:
            conn.close()

def get_default_maestro_id() -> Optional[str]:
     """Obtiene el ID del primer maestro encontrado (para MVP)."""
     conn = None
     try:
         conn = get_db_connection()
         cursor = conn.cursor()
         cursor.execute("SELECT id_maestro FROM maestros LIMIT 1")
         result = cursor.fetchone()
         return result['id_maestro'] if result else None
     except sqlite3.Error as e:
         print(f"Error SQLite al obtener default maestro ID: {e}")
         return None
     except Exception as ex:
          print(f"Error inesperado en get_default_maestro_id: {ex}")
          return None
     finally:
        if conn:
            conn.close()

# Inicializar DB al importar (asegura que exista al arrancar la app)
# init_db() # Comentado temporalmente - llamar explícitamente o al inicio de State

# Obtener ID del maestro por defecto una vez
DEFAULT_MAESTRO_ID = get_default_maestro_id()
if not DEFAULT_MAESTRO_ID:
     print("ADVERTENCIA: No se encontró un maestro por defecto en la BD. El registro de lotes podría fallar.")
     # Podrías forzar la inicialización aquí si es crítico
     # init_db()
     # DEFAULT_MAESTRO_ID = get_default_maestro_id()```

## `hackatec_2025_tecnm/utils/qr_utils.py`

```python
# camino_del_maguey/utils/qr_utils.py
import qrcode
import base64
from io import BytesIO

def generate_qr_code_base64(data: str) -> str:
    """
    Genera un código QR para los datos proporcionados y lo devuelve
    como una cadena base64 para usar en HTML/Reflex.
    """
    if not data:
        return ""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10, # Tamaño de los cuadros del QR
            border=4,   # Ancho del borde blanco
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Guardar imagen en buffer de bytes
        buffered = BytesIO()
        img.save(buffered, format="PNG")

        # Convertir a base64
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Retornar en formato Data URL
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error al generar QR para '{data}': {e}")
        return "" # Retorna cadena vacía en caso de error```

## `hackatec_2025_tecnm/pages/__init__.py`

```python
```

## `hackatec_2025_tecnm/pages/index_page.py`

```python
# camino_del_maguey/pages/index_page.py
import reflex as rx
from ..state import State # Acceder al estado desde el directorio padre

@rx.page(route="/", title="Inicio | Camino del Maguey", on_load=State.initialize_app) # Llama a init en on_load
def index() -> rx.Component:
    """Página de inicio y panel de control simple."""
    return rx.container(
        rx.vstack(
            rx.image(src="/logo_placeholder.png", width="100px", height="auto", margin_bottom="1em"), # Añadir un logo si tienes
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
                        rx.icon(tag="wifi-off" if State.is_offline_mode else "wifi", size=16, margin_left="0.5em"),
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
                             rx.icon(tag="upload-cloud", size=16, margin_left="0.5em"),
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
    )```

## `hackatec_2025_tecnm/pages/lote_viewer_page.py`

```python
# camino_del_maguey/pages/lote_viewer_page.py
import reflex as rx
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

@rx.page(route="/lotes/[lote_id]", title="Detalle del Lote | Camino del Maguey")
def lote_viewer_page() -> rx.Component:
    """Página pública que muestra la información de un lote específico."""
    return rx.container(
        # --- Evento on_mount para Cargar Datos ---
        # Usamos rx.call_script para asegurar que State.router.page.params esté disponible
        rx.script(f"console.log('Montando página para lote:', '{State.router.page.params.get('lote_id')}')"), # Debug en consola del navegador
        rx.box(on_mount=lambda: State.load_lote_data(State.router.page.params.get("lote_id", ""))),

        # --- Manejo de Carga y Errores ---
        rx.cond(
            State.is_loading_lote,
            rx.center(rx.vstack(rx.spinner(size="3"), rx.text("Cargando datos del lote...")), height="60vh")
        ),
        rx.cond(
            State.viewer_error_message & ~State.is_loading_lote,
            rx.center(
                rx.callout.root(
                    rx.callout.icon(rx.icon("alert-circle")),
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
                             rx.avatar(fallback=State.current_lote_data["nombre_maestro"][0], size="6", radius="full", high_contrast=True)
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
                                     "https://wa.me/" + State.current_lote_data["whatsapp_maestro"],
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
                     rx.text(f"URL:", rx.code_block(State.current_lote_data['url_qr_plataforma'], can_copy=True, language="text"), size="2"),
                     margin_top="2em", padding="1em", border="1px solid var(--gray-a5)", border_radius="var(--radius-2)", width="100%"
                ),

                spacing="4", width="100%", padding_bottom="3em"
            )
        ),

        # Footer simple o link de vuelta
        rx.center(rx.link("Volver al inicio", href="/", margin_top="3em", color_scheme="gray")),

        max_width="1000px", # Ancho máximo
        padding="1.5em" # Padding general
    )```

## `hackatec_2025_tecnm/pages/lotes_list_page.py`

```python
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
                                     rx.text(f"Agave: ", rx.span(lote['tipo_agave'], weight="bold")),
                                     rx.spacer(),
                                     rx.badge(lote['id_lote'].split('-')[0], color_scheme="gray"), # Mostrar parte del ID
                                     align="center", width="100%"
                                 ),
                                 href=lote['url_qr_plataforma'] # Usa la URL guardada
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
     )```

## `hackatec_2025_tecnm/pages/registration_page.py`

```python
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
            rx.input.input(
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
                 rows=rows
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
                     rx.callout.icon(rx.icon("alert-triangle")),
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
                         rx.callout.root(rx.callout.icon(rx.icon("alert-triangle")), rx.callout.text(State.form_error_message), color_scheme="red", margin_y="1em", size="1")
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
                         rx.icon(tag="wifi-off" if State.is_offline_mode else "wifi", size=16, margin_left="0.5em"),
                         on_click=State.toggle_offline_mode,
                         color_scheme=rx.cond(State.is_offline_mode, "orange", "grass"),
                         variant="soft", size="2"
                     ),
                     rx.cond(
                         State.has_pending_lotes_var,
                         rx.button(
                             f"Sincronizar ({State.pending_lotes.length()})",
                             rx.icon(tag="upload-cloud", size=16, margin_left="0.5em"),
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
    )```


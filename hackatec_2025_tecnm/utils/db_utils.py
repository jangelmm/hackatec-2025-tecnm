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
     # DEFAULT_MAESTRO_ID = get_default_maestro_id()
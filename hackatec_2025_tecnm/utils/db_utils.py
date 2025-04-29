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
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Tabla Maestros: Asegurar que Maps_url exista
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maestros (
                id_maestro TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                historia TEXT,
                whatsapp TEXT NOT NULL UNIQUE, -- Hacer whatsapp único puede ayudar a encontrar/crear
                audio_zapoteco_url TEXT,
                foto_perfil_url TEXT,
                Maps_url TEXT -- Columna para la URL de Maps
            )
        """)
        # Añadir UNIQUE constraint a whatsapp si no existe (manejo de errores básico)
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_maestro_whatsapp ON maestros(whatsapp)")
        except sqlite3.OperationalError as idx_e:
             print(f"Advertencia al crear índice UNIQUE en whatsapp (puede que ya exista): {idx_e}")


        # Tabla Lotes (sin cambios necesarios aquí)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lotes (
                id_lote TEXT PRIMARY KEY,
                id_maestro TEXT NOT NULL,
                tipo_agave TEXT NOT NULL,
                notas_cata TEXT,
                descripcion_proceso TEXT,
                fecha_produccion TEXT,
                video_yt_url TEXT,
                foto_url TEXT,
                url_qr_plataforma TEXT,
                FOREIGN KEY (id_maestro) REFERENCES maestros (id_maestro)
            )
        """)
        conn.commit()
        print(f"Base de datos inicializada/verificada en: {DB_PATH}")

        # Insertar Maestro de Ejemplo si la tabla está vacía (ya no es tan necesario)
        # Podrías comentarlo si prefieres empezar 100% desde cero con el formulario
        cursor.execute("SELECT COUNT(*) FROM maestros")
        if cursor.fetchone()[0] == 0:
            maestro_id_ejemplo = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO maestros (id_maestro, nombre, historia, whatsapp, audio_zapoteco_url, foto_perfil_url, Maps_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                maestro_id_ejemplo, "Maestro Inicial (Ejemplo)", "Agregado al iniciar la BD.", "5219510000000", None, None, None
            ))
            conn.commit()
            print(f"Maestro de ejemplo insertado con ID: {maestro_id_ejemplo}")

    except sqlite3.Error as e:
        print(f"Error durante la inicialización de la BD: {e}")
    except Exception as ex:
         print(f"Error inesperado en init_db: {ex}")
    finally:
         if conn:
            conn.close()

# ### NUEVO/MODIFICADO ### Función para encontrar o crear un maestro
def find_or_create_maestro(nombre: str, whatsapp: str, historia: str = "", maps_url: str = "") -> Optional[str]:
    """
    Busca un maestro por nombre y WhatsApp. Si no existe, lo crea.
    Retorna el ID del maestro encontrado o recién creado, o None si hay error.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Intentar encontrar por WhatsApp (más único probablemente)
        cursor.execute("SELECT id_maestro FROM maestros WHERE whatsapp = ?", (whatsapp,))
        result = cursor.fetchone()

        if result:
            print(f"Maestro encontrado por WhatsApp ({whatsapp}): ID {result['id_maestro']}")
            # Opcional: Actualizar nombre/historia/maps si se proporcionaron diferentes? (Simplificado: no actualizar)
            return result['id_maestro']
        else:
            # No encontrado, crear nuevo
            new_id = str(uuid.uuid4())
            print(f"Maestro no encontrado, creando nuevo con ID: {new_id} para {nombre} ({whatsapp})")
            cursor.execute("""
                INSERT INTO maestros (id_maestro, nombre, whatsapp, historia, Maps_url)
                VALUES (?, ?, ?, ?, ?)
            """, (new_id, nombre, whatsapp, historia, maps_url))
            conn.commit()
            return new_id

    except sqlite3.Error as e:
        print(f"Error SQLite en find_or_create_maestro: {e}")
        if conn:
            conn.rollback() # Deshacer inserción si falla el commit o algo
        return None
    except Exception as ex:
        print(f"Error inesperado en find_or_create_maestro: {ex}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def save_lote(lote_data: Dict[str, Any]) -> Optional[str]:
    """Guarda un nuevo lote en la BD y retorna su ID o None si falla."""
    id_lote = str(uuid.uuid4())
    url_qr = f"{PLATFORM_BASE_URL}/lotes/{id_lote}"
    id_maestro_asociado = lote_data.get("id_maestro") # Este ID viene de find_or_create_maestro

    if not id_maestro_asociado:
         print("Error crítico: No se proporcionó id_maestro para guardar el lote.")
         return None

    conn = None
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
            id_maestro_asociado, # Usar el ID obtenido
            lote_data.get("tipo_agave", "Agave Desconocido"),
            lote_data.get("notas_cata", ""),
            lote_data.get("descripcion_proceso", ""),
            lote_data.get("fecha_produccion", ""),
            lote_data.get("video_yt_url", ""),
            lote_data.get("foto_url", ""),
            url_qr
        ))
        conn.commit()
        print(f"Lote guardado con ID: {id_lote} asociado al maestro {id_maestro_asociado}")
        return id_lote
    except sqlite3.Error as e:
        print(f"Error SQLite al guardar lote: {e}")
        if conn: conn.rollback()
        return None
    except Exception as ex:
         print(f"Error inesperado en save_lote: {ex}")
         if conn: conn.rollback()
         return None
    finally:
        if conn: conn.close()


def get_lote_and_maestro(id_lote: str) -> Optional[Dict[str, Any]]:
    """Obtiene los datos del lote y su maestro asociado."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Asegurar que se selecciona Maps_url correctamente
        cursor.execute("""
            SELECT
                l.id_lote, l.tipo_agave, l.notas_cata, l.descripcion_proceso,
                l.fecha_produccion, l.video_yt_url, l.foto_url, l.url_qr_plataforma,
                m.id_maestro, m.nombre AS nombre_maestro, m.historia AS historia_maestro,
                m.whatsapp AS whatsapp_maestro, m.audio_zapoteco_url, m.foto_perfil_url,
                m.Maps_url -- Asegúrate que esta columna exista y se seleccione
            FROM lotes l
            JOIN maestros m ON l.id_maestro = m.id_maestro
            WHERE l.id_lote = ?
        """, (id_lote,))
        result = cursor.fetchone()
        # Convertir a dict, manejar None explícitamente
        if result:
             # print(f"Datos recuperados para lote {id_lote}: {dict(result)}") # Debug
             return dict(result)
        else:
             # print(f"No se encontró resultado para lote {id_lote}") # Debug
             return None
    except sqlite3.Error as e:
        print(f"Error SQLite al obtener lote y maestro ({id_lote}): {e}")
        return None
    except Exception as ex:
         print(f"Error inesperado en get_lote_and_maestro ({id_lote}): {ex}")
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
         cursor.execute("SELECT id_lote, tipo_agave, url_qr_plataforma FROM lotes ORDER BY rowid DESC") # Ordenar por inserción
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
# DEFAULT_MAESTRO_ID = get_default_maestro_id()
# if not DEFAULT_MAESTRO_ID:
     print("ADVERTENCIA: No se encontró un maestro por defecto en la BD. El registro de lotes podría fallar.")
     # Podrías forzar la inicialización aquí si es crítico
     # init_db()
     # DEFAULT_MAESTRO_ID = get_default_maestro_id()
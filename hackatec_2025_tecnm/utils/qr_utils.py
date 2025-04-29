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
        return "" # Retorna cadena vacía en caso de error
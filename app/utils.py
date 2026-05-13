from flask import send_from_directory, abort
import os
from app.config import UPLOAD_FOLDER

def descargar_archivo_ruta(nombre_archivo):
    if not nombre_archivo:
        abort(404, "Archivo no encontrado")
    
    ruta_completa = os.path.join(UPLOAD_FOLDER, nombre_archivo)
    if os.path.exists(ruta_completa):
        return send_from_directory(UPLOAD_FOLDER, nombre_archivo, as_attachment=True)
    else:
        abort(404, "Archivo no encontrado")
import os
from markupsafe import Markup
from flask import current_app

def inline_svg(filename):
    """Devuelve el contenido de un SVG en /static como HTML seguro"""
    
    filename = filename.lstrip("/")
    filepath = os.path.join(current_app.root_path, "static", filename)
    print("Buscando SVG en:", filepath)
    try:
        # construye ruta absoluta segura
        filepath = os.path.join(current_app.root_path, "static", filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return Markup(f.read())
    except FileNotFoundError:
        return Markup(f"<!-- SVG {filename} no encontrado -->")

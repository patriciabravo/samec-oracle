from flask import Blueprint

permisos_bp = Blueprint(
    "permisos",
    __name__,
    url_prefix="/permisos",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
from flask import Blueprint

acreditacion_bp = Blueprint(
    "acreditacion",
    __name__,
    url_prefix="/acreditacion",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
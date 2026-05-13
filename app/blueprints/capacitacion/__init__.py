from flask import Blueprint

capacitacion_bp = Blueprint(
    "capacitacion",
    __name__,
    url_prefix="/capacitacion",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
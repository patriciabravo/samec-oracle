from flask import Blueprint

autoevaluacion_bp = Blueprint(
    "autoevaluacion",
    __name__,
    url_prefix="/autoevaluacion",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
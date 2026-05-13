from flask import Blueprint

evaluacion_bp = Blueprint(
    "evaluacion",
    __name__,
    url_prefix="/evaluacion",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
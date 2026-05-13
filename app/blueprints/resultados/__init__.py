from flask import Blueprint

resultados_bp = Blueprint(
    "resultados",
    __name__,
    url_prefix="/resultados",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
from flask import Blueprint

graficos_bp = Blueprint(
    "graficos",
    __name__,
    url_prefix="/graficos",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
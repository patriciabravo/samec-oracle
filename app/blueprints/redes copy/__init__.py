from flask import Blueprint

redes_bp = Blueprint(
    "redes",
    __name__,
    url_prefix="/redes",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
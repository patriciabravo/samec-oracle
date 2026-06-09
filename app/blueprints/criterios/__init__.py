from flask import Blueprint

criterios_bp = Blueprint(
    "criterios",
    __name__,
    url_prefix="/criterios",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
from flask import Blueprint

usuario_bp = Blueprint(
    "usuario",
    __name__,
    url_prefix="/usuario",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
from flask import Blueprint

redes_bp = Blueprint(
    "ipress",
    __name__,
    url_prefix="/ipress",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
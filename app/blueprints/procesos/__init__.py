from flask import Blueprint

procesos_bp = Blueprint(
    "procesos",
    __name__,
    url_prefix="/procesos",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
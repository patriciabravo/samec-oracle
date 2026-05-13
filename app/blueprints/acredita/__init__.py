from flask import Blueprint

acredita_bp = Blueprint(
    "acredita",
    __name__,
    url_prefix="/acredita",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
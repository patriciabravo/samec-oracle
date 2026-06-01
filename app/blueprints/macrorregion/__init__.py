from flask import Blueprint

macrorregion_bp = Blueprint(
    "macrorregion",
    __name__,
    url_prefix="/macrorregion",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
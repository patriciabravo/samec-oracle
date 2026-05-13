from flask import Blueprint

calculoacredita_bp = Blueprint(
    "calculoacredita",
    __name__,
    url_prefix="/calculoacredita",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

from . import routes
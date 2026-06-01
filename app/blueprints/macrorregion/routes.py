import os
from flask import Blueprint, jsonify
from . import macrorregion_bp
from app.blueprints.macrorregion.services import (
    obtener_macrorregiones_service
)

@macrorregion_bp.route("/api/macrorregiones", methods=["GET"])
def get_macrorregiones():
    data = obtener_macrorregiones_service()
    return jsonify(data)
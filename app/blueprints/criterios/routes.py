import os
from flask import render_template, jsonify, request
from app.helpers import tiene_rol
from flask_login import login_required, current_user
from app import db
from . import redes_bp
from app.constants import ROLES
from app.constants import ROLES_NAME
from app.blueprints.redes.services import RedService

@redes_bp.route("/bandeja")
@login_required
def bandeja():
    permiso = ''
    if tiene_rol(current_user, ROLES["ROL_ADMINISTRADOR"]):
        permiso = 'add'
    return render_template("/bandeja-redes.html",permiso=permiso,lista_roles=ROLES,nombre_roles=ROLES_NAME, user=current_user,page_title="Bandeja de Redes")

@redes_bp.route('/lista', methods=['GET'])
def listar_redes():
    response = RedService.listar_redes()
    return jsonify(response), 200

@redes_bp.route('/<int:id_red>', methods=['GET'])
def obtener_red(id_red):
    response = RedService.obtener_red(id_red)    
    if not response:
        return jsonify({"message": "Red no encontrada"}), 404
    return jsonify(response), 200

@redes_bp.route('/', methods=['POST'])
def crear_red():
    data = request.get_json()
    response = RedService.crear_red(data)
    return jsonify(response), 201

@redes_bp.route('/<int:id_red>', methods=['PUT'])
def actualizar_red(id_red):
    data = request.get_json()
    response = RedService.actualizar_red(id_red, data)
    if not response:
        return jsonify({"message": "Red no encontrada"}), 404
    return jsonify(response), 200

@redes_bp.route('/<int:id_red>', methods=['DELETE'])
def eliminar_red(id_red):
    response = RedService.eliminar_red(id_red)
    if not response:
        return jsonify({"message": "Red no encontrada"}), 404
    return jsonify({"message": "Red eliminada correctamente"}), 200
import os
from flask import render_template, jsonify, request
from app.helpers import tiene_rol
from flask_login import login_required, current_user
from app import db
from . import criterios_bp
from app.constants import ROLES
from app.constants import ROLES_NAME
from app.blueprints.criterios.services import CriteriosService

@criterios_bp.route("/bandeja")
@login_required
def bandeja():
    permiso = ''
    if tiene_rol(current_user, ROLES["ROL_ADMINISTRADOR"]):
        permiso = 'add'
    return render_template("/bandeja-criterios.html",permiso=permiso,lista_roles=ROLES,nombre_roles=ROLES_NAME, user=current_user,page_title="Bandeja de Criterios")

@criterios_bp.route('/lista', methods=['GET'])
def listar_criterios():
    response = CriteriosService.listar_criterios()
    return jsonify(response), 200

@criterios_bp.route('/<int:id_criterio>', methods=['GET'])
def obtener_criterio(id_criterio):
    response = CriteriosService.obtener_criterio(id_criterio)    
    if not response:
        return jsonify({"message": "Criterio no encontrada"}), 404
    return jsonify(response), 200

@criterios_bp.route('/', methods=['POST'])
def crear_criterio():
    data = request.form
    response = CriteriosService.crear_criterio(data)
    return jsonify(response), 201

@criterios_bp.route('/<int:id_criterio>', methods=['PUT'])
def actualizar_criterio(id_criterio):
    data = request.form
    response = CriteriosService.actualizar_criterio(
        id_criterio,
        data
    )
    if not response:
        return jsonify({
            "success": False,
            "message": "Criterio no encontrado"
        }), 404
    return jsonify(response), 200

@criterios_bp.route('/<int:id_criterio>', methods=['DELETE'])
def eliminar_red(id_criterio):
    response = CriteriosService.eliminar_criterio(id_criterio)
    if not response:
        return jsonify({"message": "Criterio no encontrada"}), 404
    return jsonify({"message": "Criterio eliminado correctamente"}), 200
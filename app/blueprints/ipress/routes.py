import os
from flask import render_template, jsonify, request
from app.helpers import tiene_rol
from flask_login import login_required, current_user
from app import db
from . import ipress_bp
from app.constants import ROLES
from app.constants import ROLES_NAME
from app.blueprints.ipress.services import IpressService

@ipress_bp.route("/bandeja")
@login_required
def bandeja():
    permiso = ''
    if tiene_rol(current_user, ROLES["ROL_ADMINISTRADOR"]):
        permiso = 'add'
    return render_template("/bandeja-ipress.html",permiso=permiso,lista_roles=ROLES,nombre_roles=ROLES_NAME,user=current_user,page_title="Bandeja IPRESS")

@ipress_bp.route('/lista', methods=['GET'])
@login_required
def listar_ipress():
    response = IpressService.get_ipress_list()
    return jsonify(response), 200

@ipress_bp.route('/<int:id_ipress>', methods=['PUT'])
@login_required
def actualizar_ipress(id_ipress):
    data = request.get_json()
    print('dataaaa->',data)
    response = IpressService.actualizar_ipress(id_ipress, data)
    if response is None:
            return jsonify({"message": "Ipress no encontrada"}), 404
    return jsonify(response), 200

@ipress_bp.route('/', methods=['POST'])
def crear_ipress():
    data = request.get_json()
    response = IpressService.crear_ipress(data)
    return jsonify(response), 201

@ipress_bp.route('/<int:id_ipress>', methods=['GET'])
@login_required
def obtener_ipress(id_ipress):
    response = IpressService.obtener_ipress(id_ipress)
    if response is None:
        return jsonify({
            "success": False,
            "message": "IPRESS no encontrada"
        }), 404
    return jsonify(response), 200

####################### Ubigeo ######################
@ipress_bp.route('/<int:id_red>', methods=['DELETE'])
def eliminar_red(id_red):
    response = IpressService.eliminar_ipress(id_red)
    if not response:
        return jsonify({"message": "Ipress no encontrada"}), 404
    return jsonify({"message": "Ipress eliminada correctamente"}), 200

@ipress_bp.route('/departamentos', methods=['GET'])
def listar_departamentos():
    departamentos = IpressService.get_departamentos()
    return departamentos

@ipress_bp.route('/provincias/<int:id_departamento>', methods=['GET'])
def listar_provincias(id_departamento):
    provincias = IpressService.get_provincias(id_departamento)
    return provincias

@ipress_bp.route('/distritos/<int:id_provincia>', methods=['GET'])
def listar_distritos(id_provincia):
    distritos = IpressService.get_distritos(id_provincia)
    return distritos
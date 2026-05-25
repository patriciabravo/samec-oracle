import os
from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from . import usuario_bp
from app.helpers import tiene_roles, tiene_rol
from app.models import Usuario, Persona, Rol, RolUsuario, RedEssalud, IpressEssalud, GestorRedes
from sqlalchemy.orm import aliased
from sqlalchemy import select
from sqlalchemy import func
from app.constants import TIPOS_DOCUMENTO
from app.constants import ROLES
from app.constants import ROLES_NAME
from app.utils import descargar_archivo_ruta
from werkzeug.security import generate_password_hash
from datetime import datetime, date
from app.blueprints.usuario.services import (
    guardar_persona_service,
    obtener_usuarios_service,
    get_usuario_general_service,
    grabar_usuario_general_service,
    get_persona_service,
    get_personas_service,
    grabar_usuario_generico_service,
    get_usuario_generico_service
)

@usuario_bp.route("/bandeja")
@login_required
def bandeja_usuario():
    permiso = ''
    if tiene_rol(current_user, ROLES["ROL_ADMINISTRADOR"]):
        permiso = 'add'
    return render_template("usuario/bandeja-usuario.html",permiso=permiso,lista_roles=ROLES,nombre_roles=ROLES_NAME, user=current_user,page_title="Bandeja de Usuarios")

@usuario_bp.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    data = obtener_usuarios_service()
    return jsonify(data)

@usuario_bp.route('/grabarusuariogeneral', methods=['POST'])
def grabarusuariogeneral():
    response, status = grabar_usuario_general_service(request.form)
    return jsonify(response), status

@usuario_bp.route('/grabarusuariogenerico', methods=['POST'])
def grabarusuariogenerico():
    response, status = grabar_usuario_generico_service(
        request.form
    )
    return jsonify(response), status

@usuario_bp.route("/api/getusuariogeneral/<int:id_usuario>", methods=["GET"])
def getusuariogeneral(id_usuario):
    data = get_usuario_general_service(id_usuario)
    if not data:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(data)

@usuario_bp.route(
    "api/getusuariogenerico/<int:id_usuario>",
    methods=["GET"]
)
def getusuariogenerico(id_usuario):
    response, status = get_usuario_generico_service(
        id_usuario
    )
    return jsonify(response), status

@usuario_bp.route('/changepassword', methods=['POST'])
def changepassword():
    try:
        id_usuario = request.form.get('id_usuario_change')
        password = request.form.get('password_user')
        password_repeat = request.form.get('password_repeat_user')
        
        if password != password_repeat:
            return jsonify({"success": False, "message": "Las contraseñas no coinciden"}), 400
            
        if not password_repeat or not password:
            return jsonify({"success": False, "message": "Debe ingresar la contraseña"}), 400

        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        usuario.password = generate_password_hash(password)
        db.session.commit()

        return jsonify({"success": True, "message": "Password actualizado correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

########## ADMINISTRACION DE PERSONAS ############ 
@usuario_bp.route("/personas")
@login_required
def bandeja_personas():
    permiso = ''
    if tiene_rol(current_user, ROLES["ROL_ADMINISTRADOR"]):
        permiso = 'add'
    return render_template("usuario/bandeja-personas.html", permiso=permiso, user=current_user, page_title="Bandeja de Personas")

@usuario_bp.route('/api/personas', methods=['GET'])
def get_personas():
    data = get_personas_service()
    return jsonify(data)

@usuario_bp.route('/grabarpersona', methods=['POST'])
def grabarpersona():
    """
    Guardar persona
    ---
    tags:
      - Usuario

    responses:
      200:
        description: OK
    """
    data = request.form.to_dict(flat=True)
    response, status = guardar_persona_service(data)
    return jsonify(response), status

@usuario_bp.route("api/getpersona/<int:id_persona>", methods=["GET"])
def getpersona(id_persona):
    response, status = get_persona_service(id_persona)
    return jsonify(response), status

################### OTROS ###################################
@usuario_bp.route("/descargar/<int:id_usuario>")
def descargar_usuario(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    return descargar_archivo_ruta(usuario.ruta_archivo_autorizacion)
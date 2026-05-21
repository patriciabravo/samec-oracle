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
from app.utils import descargar_archivo_ruta
from werkzeug.security import generate_password_hash
from datetime import datetime, date
from app.blueprints.usuario.services import guardar_persona_service

@usuario_bp.route("/bandeja")
@login_required
def bandeja_usuario():
    return render_template("usuario/bandeja-usuario.html", roles=ROLES, user=current_user, page_title="Administración de Usuarios")

@usuario_bp.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    stmt = (
    db.session.query(
        Usuario.id_usuario,
        Usuario.username,
        (Persona.nombres +  ' ' + Persona.apellido_paterno + ' ' + Persona.apellido_materno).label('nombres_completos'),
        Persona.tipo_documento,
        Persona.numero_documento,
        Usuario.correo,
        Rol.id_rol,
        Rol.nombre_rol.label('rol'),
        RedEssalud.nombre_red,
        IpressEssalud.nombre_ipress,
        Usuario.fecha_registro,
        Usuario.activo
        )
        .outerjoin(Persona, Usuario.id_persona == Persona.id_persona)
        .outerjoin(RolUsuario, RolUsuario.id_usuario == Usuario.id_usuario)
        .outerjoin(Rol, Rol.id_rol == RolUsuario.id_rol)
        .outerjoin(RedEssalud, Usuario.id_red == RedEssalud.id_red)
        .outerjoin(IpressEssalud, Usuario.id_ipress == IpressEssalud.id_ipress)
        .order_by(Persona.id_persona)
    )
    results = db.session.execute(stmt).mappings().all()
    data = []
    for row in results:
        d = dict(row)
        try:
            tipo_doc = int(d["tipo_documento"])
        except (TypeError, ValueError):
            tipo_doc = None
        d["tipo_documento_texto"] = TIPOS_DOCUMENTO.get(tipo_doc, "Desconocido")
        d["fecha_registro"] = d["fecha_registro"].strftime("%Y-%m-%d")              
        data.append(d)
    return jsonify(data)

@usuario_bp.route('/grabarusuariogeneral', methods=['POST'])
def grabarusuariogeneral():
    try:
        username = request.form.get('username')
        correo  = request.form.get('correo')
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')
        id_usuario = request.form.get('id_usuario')
        id_rol = request.form.get('sel_rol_essalud')
        red_jefe_calidad = request.form.get('sel_red')
        redes_asignadas = request.form.getlist('sel_redes_asignadas')
        sel_persona = request.form.getlist('select_persona')
        estado = request.form.get('estado')

        if not id_usuario:
            if password != password_repeat:
                return jsonify({"success": False, "message": "Las contraseñas no coinciden"}), 400
                
            if not password:
                return jsonify({"success": False, "message": "Contraseña es requerida"}), 400

        if not correo:
            return jsonify({"success": False, "message": "Correo es requerido"}), 400

        ## el usuario nuevo ##
        if  not id_usuario:
            existe_correo = Usuario.query.filter_by(correo=correo).first()
            if existe_correo:
                return jsonify({"success": False, "message": "Correo ya esta registrado"}), 201

            nuevo_usuario = Usuario(
                id_persona=sel_persona[0],
                username=username,
                password=generate_password_hash(password),
                correo=correo,
                activo=bool(estado),
                fecha_registro=datetime.now()
            )
            db.session.add(nuevo_usuario)
            mensaje = "Usuario registrada correctamente"
            db.session.flush()
            actual_id_usuario = nuevo_usuario.id_usuario

        ## el usuario ya existe
        else:
            usuario_insert = Usuario.query.get(id_usuario)
            if not usuario_insert:
                return jsonify({"success": False, "error": "Usuario no encontrado"})
            usuario_insert.id_persona=sel_persona[0],
            usuario_insert.username=username,
            usuario_insert.correo=correo,
            usuario_insert.activo=bool(estado),
            usuario_insert.fecha_registro=datetime.now()
            mensaje = "Usuario actualizada correctamente"
            actual_id_usuario = usuario_insert.id_usuario

        ##Elimino los roles asignadas
        RolUsuario.query.filter_by(id_usuario=actual_id_usuario).delete()
        nuevo_rol = RolUsuario(id_usuario=actual_id_usuario,id_rol=id_rol[0],fecha_asignacion=datetime.now())
        db.session.add(nuevo_rol)

        ##Elimino las redes asignadas y inserto si hay un array
        GestorRedes.query.filter_by(id_usuario=actual_id_usuario).delete()
        if redes_asignadas:
            for id_red in redes_asignadas:
                nueva_relacion = GestorRedes(id_usuario=actual_id_usuario, id_red=id_red)
                db.session.add(nueva_relacion)

        db.session.commit()
        return jsonify({"success": True, "message": "Usuario actualizado correctamente"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@usuario_bp.route('/grabarusuariogenerico', methods=['POST'])
def grabarusuariogenerico():
    try:
        id_usuario =  request.form.get('id_usuario_generico') 
        username = request.form.get('username_generico')
        password = request.form.get('password2')
        password_repeat = request.form.get('password_repeat2')       
        correo  = request.form.get('correo_generico')
        id_rol = request.form.get('sel_rol_essalud_generico')
        id_ipress = request.form.get('sel_ipress')
        estado = request.form.getlist('estado_user_ipress')
        activo = bool(int(estado[0])) if estado else False

        if not correo:
            return jsonify({"success": False, "message": "Correo es requerido"}), 400

        if not id_usuario:    
            existe_correo = Usuario.query.filter_by(correo=correo).first()
            if existe_correo:
                return jsonify({"success": False, "message": "Correo ya esta registrado"}), 201
        if not id_usuario:
            if password != password_repeat:
                return jsonify({"success": False, "message": "Las contraseñas no coinciden"}), 400
                
            if not password:
                return jsonify({"success": False, "message": "Contraseña es requerida"}), 400    

            nuevo_usuario = Usuario(           
                username=username,
                password=generate_password_hash(password),
                correo=correo,
                activo=activo,
                id_ipress=id_ipress,
                fecha_registro=datetime.now()
            )
            db.session.add(nuevo_usuario)
            db.session.flush()
        else:
            usuario_generico = Usuario.query.get(id_usuario)
            if username: usuario_generico.username = username
            if correo: usuario_generico.correo = correo
            if id_ipress: usuario_generico.id_ipress = id_ipress
            if estado: usuario_generico.activo =  bool(int(estado[0]))

        if not id_usuario:
            rol_usuario = RolUsuario(
                id_usuario=nuevo_usuario.id_usuario,
                id_rol=id_rol,
                fecha_asignacion=datetime.now()
            )
            db.session.add(rol_usuario)
        else:
            rol_usuario = RolUsuario.query.filter_by(id_usuario=id_usuario).first()
            rol_usuario.id_rol = id_rol

        db.session.commit()

        return jsonify({"success": True, "message": "Usuario actualizado correctamente"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@usuario_bp.route("api/getusuariogeneral/<int:id_usuario>", methods=["GET"])
def getusuariogeneral(id_usuario):
	stmt = (
		select(
			Usuario.id_usuario,
            Usuario.username,
            Usuario.activo,
            RolUsuario.id_rol,
            Persona.id_persona,       
			Persona.nombres,
			Persona.apellido_paterno,
			Persona.apellido_materno,
			Persona.tipo_documento,
			Persona.numero_documento,
			Usuario.password,
			Usuario.correo
		)
		.join(Usuario, Usuario.id_persona == Persona.id_persona)
        .join(RolUsuario, RolUsuario.id_usuario == Usuario.id_usuario)
		.where(Usuario.id_usuario == id_usuario)        
	)
	result = db.session.execute(stmt).first()
	if not result:
		return jsonify({"error": "Usuario no encontrado"}), 404

	data = {
		"nombres": result.nombres,
		"apellido_paterno": result.apellido_paterno,
		"apellido_materno": result.apellido_materno,
        "usuario": result.username,
		"tipo_documento": result.tipo_documento,
		"numero_documento": result.numero_documento,
		"id_usuario": result.id_usuario,
        "id_persona": result.id_persona,
        "id_rol": result.id_rol, 
		"correo": result.correo,
        "activo": result.activo
		}
	return jsonify(data)

@usuario_bp.route("api/getusuariogenerico/<int:id_usuario>", methods=["GET"])
def getusuariogenerico(id_usuario):
    stmt = (
        select(
            Usuario.id_usuario,
            Usuario.username,
            Usuario.correo,
            Rol.nombre_rol.label('rol'),
            Rol.id_rol,
            IpressEssalud.id_ipress,
            IpressEssalud.nombre_ipress,
            Usuario.fecha_registro,
            Usuario.activo
        )
        .outerjoin(RolUsuario, RolUsuario.id_usuario == Usuario.id_usuario)
        .outerjoin(Rol, Rol.id_rol == RolUsuario.id_rol)
        .outerjoin(IpressEssalud, IpressEssalud.id_ipress == Usuario.id_ipress)
        .filter(Usuario.id_usuario == id_usuario)        
    )
    result = db.session.execute(stmt).first()
    if not result:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = {
        'id_usuario': result.id_usuario,
        'username': result.username,
        'correo': result.correo,
        'rol': result.rol,
        'id_rol': result.id_rol,
        'id_ipress': result.id_ipress,
        'nombre_ipress': result.nombre_ipress,
        'fecha_registro': result.fecha_registro,
        'activo': result.activo
	}
    return jsonify(data)

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
    stmt = (
    db.session.query(
        Persona.id_persona,
        (Persona.nombres +  ' ' + Persona.apellido_paterno + ' ' + Persona.apellido_materno).label('nombres_completos'),
        Persona.nombres,
        Persona.apellido_paterno,
        Persona.apellido_materno,
        Persona.tipo_documento,
        Persona.numero_documento,
        Persona.fecha_registro,
        func.to_char(Persona.fecha_registro, 'DD/MM/YYYY HH24:MI:SS').label('fecha_registro_formato')
        )
        .order_by(Persona.id_persona)
    )
    results = db.session.execute(stmt).mappings().all()
    data = []
    for row in results:
        d = dict(row)
        try:
            tipo_doc = int(d["tipo_documento"])
        except (TypeError, ValueError):
            tipo_doc = None
        d["tipo_documento_texto"] = TIPOS_DOCUMENTO.get(tipo_doc, "Desconocido")           
        data.append(d)
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

""" @usuario_bp.route('/grabarpersona', methods=['POST'])
def grabarpersona():
    data = request.form.to_dict(flat=True)
    id_persona = data.get('id_persona')
    nombres = data.get('nombres')
    apellido_paterno = data.get('apellido_paterno')
    apellido_materno = data.get('apellido_materno')
    tipo_documento = data.get('tipo_documento')
    numero_documento = data.get('numero_documento')
    try:
        if id_persona:
            persona = Persona.query.get(id_persona)
            if not persona:
                return jsonify({'success': False, 'error': 'Persona no encontrada'}), 404
            persona.nombres = nombres
            persona.apellido_paterno = apellido_paterno
            persona.apellido_materno = apellido_materno
            persona.tipo_documento = tipo_documento
            persona.numero_documento = numero_documento
            mensaje = 'Persona actualizada correctamente'
        else:
            persona_existente = Persona.query.filter_by(numero_documento=numero_documento).first()
            if persona_existente:
                return jsonify({'success': False, 'error': 'El número de documento ya existe'}), 400
            persona = Persona(
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                tipo_documento=tipo_documento,
                numero_documento=numero_documento
            )
            db.session.add(persona)
            mensaje = 'Persona registrada correctamente'

        db.session.commit()
        return jsonify({'success': True, 'mensaje': mensaje})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500  """

@usuario_bp.route("api/getpersona/<int:id_persona>", methods=["GET"])
def getpersona(id_persona):
	stmt = (
		select(
            Persona.id_persona,
			Persona.nombres,
			Persona.apellido_paterno,
			Persona.apellido_materno,
			Persona.tipo_documento,
			Persona.numero_documento
		)
		.where(Persona.id_persona == id_persona)        
	)
	result = db.session.execute(stmt).first()
	if not result:
		return jsonify({"error": "Usuario no encontrado"}), 404

	data = {
		"nombres": result.nombres,
		"apellido_paterno": result.apellido_paterno,
		"apellido_materno": result.apellido_materno,
		"tipo_documento": result.tipo_documento,
		"numero_documento": result.numero_documento,
        "id_persona": result.id_persona,
		}
	return jsonify(data)

########## OTROS ############
@usuario_bp.route("/descargar/<int:id_usuario>")
def descargar_usuario(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)
    return descargar_archivo_ruta(usuario.ruta_archivo_autorizacion)
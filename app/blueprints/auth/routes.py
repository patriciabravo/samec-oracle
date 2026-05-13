import os
import secrets
import json
from flask import render_template, request, redirect, url_for, jsonify, current_app
from app import db
from . import auth_bp
from flask_login import current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import Persona, Usuario, RedEssalud, IpressEssalud,RolUsuario
from datetime import datetime, date
from flask_login import logout_user
from flask import redirect, url_for
UPLOAD_FOLDER = "uploads"  # carpeta dentro de tu proyecto
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@auth_bp.route('/register', methods=["GET","POST"])
def register():
    return render_template("auth/sign-up.html")

@auth_bp.route('/uploadregistro', methods=["GET","POST"])
def uploadregistro():
    if request.method == 'POST':
        file = request.files['file']
        random_file_name = secrets.token_hex(8)
        filename = secure_filename(file.filename)  # nombre original limpio
        ext = os.path.splitext(filename)[1]
        random_filename = f"{random_file_name}{ext}"        
        if not allowed_file(filename):
            return jsonify({"error": "Solo se permiten archivos PDF"}), 400

        project_root = os.path.dirname(current_app.root_path)
        upload_path = os.path.join(project_root, 'uploads')
        os.makedirs(upload_path, exist_ok=True)        
        # guardar en disco con random_name
        file.save(os.path.join(upload_path, random_filename))      

        print('File successfully uploaded ' + file.filename + ' to the database!')
        msg = 'Success Upload'    
    return jsonify({"message":msg, "real_filename": filename, "upload_filename": random_filename})

@auth_bp.route("/delete-file/<file_name>", methods=["DELETE"])
def delete_file(file_name):
    try:
        # Construir ruta completa
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        # Validar existencia
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True, "message": "Archivo eliminado"}), 200
        else:
            return jsonify({"success": False, "message": "Archivo no encontrado"}), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

def asignar_rol(id_red=None, id_ipress=None):
# Si existe id_red y id_ipress => rol = 2
# Si existe solo id_red y no id_ipress => rol = 1
# Si existe solo id_red y id_red == 3 => rol = 3
    rol_id = 1
    if id_red is not None and id_ipress is not None:
        rol_id = 2
    elif id_red is not None and id_ipress is None and id_red == 3:
        rol_id = 3
    return rol_id

@auth_bp.route('/guardausuario', methods=["POST"])
def guardausuario():
        try:
            tipo_doc = request.form.get("tipo_doc")
            nro_documento = request.form.get("nro_documento")
            nombres  = request.form.get("nombres")
            apellido_paterno  = request.form.get("apellido_paterno")
            apellido_materno  = request.form.get("apellido_materno")              
            id_red = request.form.get("redes")
            id_ipress = request.form.get("ipress")
            correo = request.form.get("correo")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm-password")
            file_data = request.form.get("filesToInsertDB")                
            if not file_data:
                return jsonify({
                    "success": False,
                    "message": "No se recibio archivo"
                    }), 400
            file_info = json.loads(file_data)
            real_filename = file_info.get("real_filename")
            upload_filename = file_info.get("upload_filename")

            if password != confirm_password:
                return jsonify({
                    "success": False,
                    "message": "Las contraseñas no coinciden"
                    }), 400
            
            if not correo or not password:
                return jsonify({
                    "success": False,
                    "message": "Correo y contraseña son requeridos"
                    }), 400
            
            existe_correo = Usuario.query.filter_by(correo=correo).first()
            if existe_correo:
                return jsonify({
                    "success": False,
                    "message": "Correo ya esta registrado"                    
                }), 201

            
            # Buscar persona por tipo y número de documento
            persona = Persona.query.filter_by(
                tipo_documento=tipo_doc,
                numero_documento=nro_documento
            ).first()

            if not persona:
                # Crear persona
                nueva_persona = Persona(
                    tipo_documento=tipo_doc,
                    numero_documento=nro_documento,
                    nombres=nombres,
                    apellido_paterno=apellido_paterno,
                    apellido_materno=apellido_materno,
                    fecha_registro=datetime.now()               
                )
                db.session.add(nueva_persona)
                db.session.flush()  # para obtener el id_persona sin hacer commit aún
                id_persona_relacionada = nueva_persona.id_persona
            else:
                id_persona_relacionada = persona.id_persona

            # Crear usuario asociado
            nuevo_usuario = Usuario(
                password=generate_password_hash(password),
                id_persona=id_persona_relacionada,
                estado=0,
                activo=False,
                fecha_registro=datetime.now(),
                archivo_autorizacion=real_filename,
                correo=correo,
                ruta_archivo_autorizacion=upload_filename,
                id_red=id_red,
                id_ipress=id_ipress
            )
            db.session.add(nuevo_usuario)
            db.session.flush()

            id_rol = asignar_rol(id_red, id_ipress)
            rol_usuario = RolUsuario(
                id_usuario=nuevo_usuario.id_usuario,
                id_rol=id_rol,
                fecha_asignacion=datetime.now()
            )
            db.session.add(rol_usuario)
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Felicidades su usuario ha sido creado correctamente",
                "persona_id": id_persona_relacionada,
                "usuario_id": nuevo_usuario.id_usuario
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500


@auth_bp.route('/logueo', methods=["GET","POST"])
def logueo():
    if request.method == "GET":
        return render_template("auth/sign-in.html")
    else:
        usuario = request.form.get("usuario")
        password = request.form.get("password")        
        if not usuario or not password:
            return jsonify({"success": False, "message": "Usuario y contraseña son requeridos"}), 400

        usuario = Usuario.query.filter_by(username=usuario).first()
        if usuario:
            if not Usuario.activo:  #usuario inactivo
                return jsonify({"success": False, "message": "Usuario inactivo"}), 401
            else:
                if not check_password_hash(usuario.password, password):
                    return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401
                else:
                    login_user(usuario)  # login_user es de flask_login
                    return jsonify({"success": True, "redirect_url": url_for("dashboard.home")})
        else:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 401

#API simulada: Tipos de documento
@auth_bp.route("/tipos-documento", methods=["GET"])
def tipos_documento():
    data = [
        {"id": 1, "nombre": "DNI"},
        {"id": 2, "nombre": "Carnet de Extranjería"},
        {"id": 3, "nombre": "Pasaporte"}
    ]
    return jsonify(data)

@auth_bp.route("/redes-essalud", methods=["GET"])
def get_redes_essalud():
    redes = db.session.query(RedEssalud.id_red, RedEssalud.nombre_red).all()
    data = [
        {"id": r.id_red, "nombre": r.nombre_red}
        for r in redes
    ]
    return jsonify(data)

@auth_bp.route("/ipress-essalud/<int:id_red>",  methods=["GET"])
def get_ipress_essalud(id_red):
    ipresses = (
        db.session.query(IpressEssalud.id_ipress, IpressEssalud.nombre_ipress)
        .filter(IpressEssalud.id_red == id_red)
        .all()
    )
    data = [
        {"id": i.id_ipress, "nombre": i.nombre_ipress}
        for i in ipresses
    ]
    return jsonify(data)


@auth_bp.route('/logout')
def logout():
    logout_user()     # Cierra sesión limpiamente
    return redirect(url_for('auth.logueo'))  # Te envía al login

from flask_login import login_required, current_user


@auth_bp.route('/perfil/cambiar-password', methods=['POST'])
@login_required
def cambiar_password_perfil():
    try:
        password_actual = request.form.get("password_actual")
        nuevo_password = request.form.get("nuevo_password")
        confirmar_password = request.form.get("confirmar_password")

        if not password_actual or not nuevo_password or not confirmar_password:
            return jsonify({
                "success": False,
                "message": "Todos los campos de contraseña son obligatorios"
            }), 400

        if not check_password_hash(current_user.password, password_actual):
            return jsonify({
                "success": False,
                "message": "El password actual es incorrecto"
            }), 400

        if nuevo_password != confirmar_password:
            return jsonify({
                "success": False,
                "message": "El nuevo password no coincide"
            }), 400

        if len(nuevo_password) < 8:
            return jsonify({
                "success": False,
                "message": "El password debe tener al menos 8 caracteres"
            }), 400

        current_user.password = generate_password_hash(nuevo_password)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Password actualizado correctamente"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    
@auth_bp.app_context_processor
def inject_user_role():
    if not current_user.is_authenticated:
        return {}

    rol = (
        db.session.query(RolUsuario)
        .filter(RolUsuario.id_usuario == current_user.id_usuario)
        .first()
    )

    nombre_rol = ""
    if rol and rol.rol:
        nombre_rol = rol.rol.nombre_rol

    return dict(current_user_rol=nombre_rol)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'jpg'}

def allowed_file_hito(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf'}


@auth_bp.route('/uploadevidencia', methods=["GET","POST"])
def uploadevidencia():
    if request.method == 'POST':
        
        print("FILES:", request.files)        
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file received'}), 400
        random_file_name = secrets.token_hex(8)
        filename = secure_filename(file.filename)  # nombre original limpio
        ext = os.path.splitext(filename)[1]
        random_filename = f"{random_file_name}{ext}"        
        if not allowed_file(filename):
            return jsonify({"error": "Solo se permiten archivos JPG"}), 400

        project_root = os.path.dirname(current_app.root_path)
        upload_path = os.path.join(project_root, 'uploads/temp_fuentes/')
        os.makedirs(upload_path, exist_ok=True)        
        # guardar en disco con random_name
        file.save(os.path.join(upload_path, random_filename))      

        print('File successfully uploaded ' + file.filename + ' to the database!')
        msg = 'Success Upload'    
    return jsonify({"message":msg, "real_filename": filename, "upload_filename": random_filename})


@auth_bp.route("/delete-evidencia/<file_name>", methods=["DELETE"])
def delete_evidencia(file_name):
    try:
        # Construir ruta completa
        file_path = os.path.join(UPLOAD_FOLDER, 'temp_fuentes/'+file_name)
        print(file_path)
        # Validar existencia
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True, "message": "Archivo eliminado"}), 200
        else:
            return jsonify({"success": False, "message": "Archivo no encontrado"}), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@auth_bp.route('/uploadhito', methods=["GET","POST"])
def uploadhito():
    if request.method == 'POST':        
        print("FILES:", request.files)        
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No file received'}), 400
        random_file_name = secrets.token_hex(8)
        filename = secure_filename(file.filename)  # nombre original limpio
        ext = os.path.splitext(filename)[1]
        random_filename = f"{random_file_name}{ext}"        
        if not allowed_file_hito(filename):
            return jsonify({"error": "Solo se permiten archivos PDF"}), 400
        project_root = os.path.dirname(current_app.root_path)
        upload_path = os.path.join(project_root, 'uploads/temp_fuentes/')
        os.makedirs(upload_path, exist_ok=True)        
        # guardar en disco con random_name
        file.save(os.path.join(upload_path, random_filename))      

        print('File successfully uploaded ' + file.filename + ' to the database!')
        msg = 'Success Upload'    
    return jsonify({"message":msg, "real_filename": filename, "upload_filename": random_filename})
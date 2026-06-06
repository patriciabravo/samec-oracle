from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash
from app.models import Usuario, Persona, Rol, RolUsuario, RedEssalud, IpressEssalud, GestorRedes
from sqlalchemy import literal
from sqlalchemy import select
from sqlalchemy import func
from app.constants import TIPOS_DOCUMENTO
from app.constants import ROLES


def guardar_persona_service(data):

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
                return {
                    'success': False,
                    'error': 'Persona no encontrada'
                }, 404
            persona.nombres = nombres
            persona.apellido_paterno = apellido_paterno
            persona.apellido_materno = apellido_materno
            persona.tipo_documento = tipo_documento
            persona.numero_documento = numero_documento
            mensaje = 'Persona actualizada correctamente'
        else:
            persona_existente = Persona.query.filter_by(
                numero_documento=numero_documento
            ).first()
            if persona_existente:
                return {
                    'success': False,
                    'error': 'El número de documento ya existe'
                }, 400
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
        return {
            'success': True,
            'mensaje': mensaje
        }, 200
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }, 500
              
def obtener_usuarios_service():
    stmt = (
        db.session.query(
            Usuario.id_usuario,
            Usuario.username,
            Usuario.id_persona,
            (Persona.nombres + literal(' ') + Persona.apellido_paterno + literal(' ') + Persona.apellido_materno).label('nombres_completos'),
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
        .outerjoin(Persona, Persona.id_persona == Usuario.id_persona )
        .outerjoin(RolUsuario, RolUsuario.id_usuario == Usuario.id_usuario)
        .outerjoin(Rol, Rol.id_rol == RolUsuario.id_rol)
        .outerjoin(RedEssalud, Usuario.id_red == RedEssalud.id_red)
        .outerjoin(IpressEssalud, Usuario.id_ipress == IpressEssalud.id_ipress)
        .order_by(Persona.id_persona)
    )    
    '''print(
        stmt.statement.compile(
            dialect=db.engine.dialect,
            compile_kwargs={"literal_binds": True}
        )
    )'''
    results = db.session.execute(stmt).mappings().all()
    data = []
    for row in results:
        d = dict(row)
        try:
            tipo_doc = int(d["tipo_documento"])
        except (TypeError, ValueError):
            tipo_doc = None
        d["tipo_documento_texto"] = TIPOS_DOCUMENTO.get(tipo_doc,"")
        if d["fecha_registro"]:
            d["fecha_registro"] = d["fecha_registro"].strftime("%Y-%m-%d")
        data.append(d)
    return data

def get_usuario_general_service(id_usuario):
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
            Usuario.id_red,
            Usuario.id_ipress,           
            Usuario.correo
        )
        .join(Usuario, Usuario.id_persona == Persona.id_persona)
        .join(RolUsuario, RolUsuario.id_usuario == Usuario.id_usuario)
        .where(Usuario.id_usuario == id_usuario)
    )
    result = db.session.execute(stmt).first()
    if not result:
        return None
    
    ids_redes = []    
    if (result.id_rol == ROLES["ROL_GESTOR_GAMCC"]):
        redes = (
            db.session.query(GestorRedes.id_red)
            .filter(GestorRedes.id_usuario == id_usuario)
            .all()
        )
        ids_redes = [r.id_red for r in redes]
    
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
        "id_red": result.id_red,
        "id_ipress": result.id_ipress,
        "correo": result.correo,
        "redes_asignadas": ids_redes,
        "activo": result.activo
    }
    return data

def grabar_usuario_general_service(form):
    try:
        username = form.get('username')
        correo = form.get('correo')
        password = form.get('password')
        password_repeat = form.get('password_repeat')
        id_usuario = form.get('id_usuario')
        id_rol = form.get('sel_rol_essalud')
        sel_red = form.get('sel_red')
        sel_ipress = form.get('sel_ipress')
        redes_asignadas = form.getlist('sel_redes_asignadas')
        sel_persona = form.get('select_persona')        
        estado = form.get('estado')

        print(form.to_dict(flat=False))
        print(redes_asignadas)
        
        if not id_usuario:
            if password != password_repeat:
                return {
                    "success": False,
                    "message": "Las contraseñas no coinciden"
                }, 400
            if not password:
                return {
                    "success": False,
                    "message": "Contraseña es requerida"
                }, 400

        if not correo:
            return {
                "success": False,
                "message": "Correo es requerido"
            }, 400
        id_red_insert = None
        if id_rol == str(ROLES["ROL_RED"]):
            id_red_insert = sel_red

        # NUEVO USUARIO
        if not id_usuario:
            existe_correo = Usuario.query.filter_by(
                correo=correo
            ).first()
            if existe_correo:
                return {
                    "success": False,
                    "message": "Correo ya esta registrado"
                }, 201
            nuevo_usuario = Usuario(
                id_persona=sel_persona,
                username=username,
                password=generate_password_hash(password),
                correo=correo,
                id_red=id_red_insert,
                id_ipress=sel_ipress,
                activo=estado,
                fecha_registro=datetime.now()
            )
            db.session.add(nuevo_usuario)
            db.session.flush()
            actual_id_usuario = nuevo_usuario.id_usuario
            mensaje = "Usuario registrado correctamente"
        # ACTUALIZAR USUARIO
        else:
            usuario_insert = Usuario.query.get(id_usuario)
            if not usuario_insert:
                return {
                    "success": False,
                    "error": "Usuario no encontrado"
                }, 404
            usuario_insert.id_persona = sel_persona
            usuario_insert.username = username
            usuario_insert.correo = correo
            usuario_insert.activo = estado
            usuario_insert.id_red = id_red_insert
            usuario_insert.id_ipress = sel_ipress
            usuario_insert.fecha_registro = datetime.now()
            actual_id_usuario = usuario_insert.id_usuario
            mensaje = "Usuario actualizado correctamente"
        # ACTUALIZAR ROL
        rol_usuario = RolUsuario.query.filter_by(
            id_usuario=actual_id_usuario
        ).first()
        if rol_usuario:
            rol_usuario.id_rol = id_rol
            rol_usuario.fecha_asignacion = datetime.now()
        else:
            nuevo_rol = RolUsuario(
                id_usuario=actual_id_usuario,
                id_rol=id_rol,
                fecha_asignacion=datetime.now()
            )
            db.session.add(nuevo_rol)
        # ELIMINAR REDES ANTERIORES
        GestorRedes.query.filter_by(
            id_usuario=actual_id_usuario
        ).delete()
        # INSERTAR NUEVAS REDES
        if redes_asignadas:
            for id_red in redes_asignadas:
                nueva_relacion = GestorRedes(
                    id_usuario=actual_id_usuario,
                    id_red=id_red
                )
                print(nueva_relacion)
                db.session.add(nueva_relacion)
                
        db.session.commit()
        return {
            "success": True,
            "message": mensaje
        }, 200
    except Exception as e:
        print(str(e))
        db.session.rollback()
        return {
            "success": False,
            "error": str(e)
        }, 500

def grabar_usuario_generico_service(form):
    try:
        id_usuario = form.get('id_usuario_generico')
        username = form.get('username_generico')
        password = form.get('password2')
        password_repeat = form.get('password_repeat2')
        correo = form.get('correo_generico')
        id_rol = form.get('sel_rol_essalud_generico')
        id_ipress = form.get('sel_ipress')
        estado = form.getlist('estado_user_ipress')
        activo = bool(int(estado[0])) if estado else False
        if not correo:
            return {
                "success": False,
                "message": "Correo es requerido"
            }, 400
        if not id_usuario:
            existe_correo = Usuario.query.filter_by(
                correo=correo
            ).first()
            if existe_correo:
                return {
                    "success": False,
                    "message": "Correo ya esta registrado"
                }, 201
        if not id_usuario:
            if password != password_repeat:
                return {
                    "success": False,
                    "message": "Las contraseñas no coinciden"
                }, 400
            if not password:
                return {
                    "success": False,
                    "message": "Contraseña es requerida"
                }, 400
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
            if not usuario_generico:
                return {
                    "success": False,
                    "message": "Usuario no encontrado"
                }, 404
            if username:
                usuario_generico.username = username
            if correo:
                usuario_generico.correo = correo
            if id_ipress:
                usuario_generico.id_ipress = id_ipress
            if estado:
                usuario_generico.activo = bool(
                    int(estado[0])
                )
        if not id_usuario:
            rol_usuario = RolUsuario(
                id_usuario=nuevo_usuario.id_usuario,
                id_rol=id_rol,
                fecha_asignacion=datetime.now()
            )
            db.session.add(rol_usuario)
        else:
            rol_usuario = RolUsuario.query.filter_by(
                id_usuario=id_usuario
            ).first()
            if rol_usuario:
                rol_usuario.id_rol = id_rol
                rol_usuario.fecha_asignacion = datetime.now()
            else:
                nuevo_rol = RolUsuario(
                    id_usuario=id_usuario,
                    id_rol=id_rol,
                    fecha_asignacion=datetime.now()
                )
                db.session.add(nuevo_rol)
        db.session.commit()
        return {
            "success": True,
            "message": "Usuario actualizado correctamente"
        }, 200
    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "error": str(e)
        }, 500
 
def get_usuario_generico_service(id_usuario):
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
        .outerjoin(
            RolUsuario,
            RolUsuario.id_usuario == Usuario.id_usuario
        )
        .outerjoin(
            Rol,
            Rol.id_rol == RolUsuario.id_rol
        )
        .outerjoin(
            IpressEssalud,
            IpressEssalud.id_ipress == Usuario.id_ipress
        )
        .filter(Usuario.id_usuario == id_usuario)
    )
    result = db.session.execute(stmt).first()
    if not result:
        return {
            "error": "Usuario no encontrado"
        }, 404
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
    return data, 200
       
def get_personas_service():
    stmt = (
        db.session.query(
            Persona.id_persona,
            (
                Persona.nombres + ' ' +
                Persona.apellido_paterno + ' ' +
                Persona.apellido_materno
            ).label('nombres_completos'),
            Persona.nombres,
            Persona.apellido_paterno,
            Persona.apellido_materno,
            Persona.tipo_documento,
            Persona.numero_documento,
            Persona.fecha_registro,
            func.to_char(
                Persona.fecha_registro,
                'DD/MM/YYYY HH24:MI:SS'
            ).label('fecha_registro_formato')
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
        d["tipo_documento_texto"] = TIPOS_DOCUMENTO.get(
            tipo_doc,
            "Desconocido"
        )
        data.append(d)
    return data

def get_persona_service(id_persona):
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
        return {
            "error": "Usuario no encontrado"
        }, 404
    data = {
        "nombres": result.nombres,
        "apellido_paterno": result.apellido_paterno,
        "apellido_materno": result.apellido_materno,
        "tipo_documento": result.tipo_documento,
        "numero_documento": result.numero_documento,
        "id_persona": result.id_persona
    }
    return data, 200
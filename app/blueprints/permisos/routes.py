from . import permisos_bp
from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from collections import defaultdict
from app.models import RolOpcion, Opcion, Menu, Rol
from app.models import RedEssalud
from app.models import IpressEssalud
from app import db
from sqlalchemy import func, cast, String



@permisos_bp.route("/menus", methods=['GET'])
@login_required
def menus():
    return render_template("permisos/menus.html", user=current_user, page_title="Listado de Menus")


@permisos_bp.route("/configura", methods=['GET'])
@login_required
def configuramenus():
    return render_template("permisos/configuramenu.html", user=current_user, page_title="Configura Menus por Rol")

@permisos_bp.route("api/getlistaroles", methods=["GET"])
def getlistaroles():
    query = (
        db.session.query(
            Rol.id_rol,
            Rol.nombre_rol,
            func.string_agg(
                func.concat(Menu.nombre_menu, ' - ', Opcion.nombre_opcion),
                ';'
            ).label('opciones_rol'),
            func.string_agg(
                cast(Opcion.id_opcion, String),
                ';'
            ).label('arr_opciones')
        )
        .outerjoin(RolOpcion, Rol.id_rol == RolOpcion.id_rol)
        .outerjoin(Opcion, RolOpcion.id_opcion == Opcion.id_opcion)
        .outerjoin(Menu, Menu.id_menu == Opcion.id_menu)
        .group_by(Rol.id_rol, Rol.nombre_rol)
    )
    resultados = query.all()
    data = [
        {
            "id_rol": r.id_rol,
            "nombre_rol": r.nombre_rol,
            "opciones_rol": r.opciones_rol,
            "arr_opciones": r.arr_opciones
        }
        for r in resultados
    ]
    return jsonify(data)

@permisos_bp.route("api/getallopciones", methods=["GET"])
def getallopciones():
    resultados = (
        db.session.query(
            Opcion.id_opcion,
            func.concat(Menu.nombre_menu, ' - ', Opcion.nombre_opcion).label('opciones_rol')
        )
        .outerjoin(Menu, Menu.id_menu == Opcion.id_menu)
        .filter(Opcion.activo == 1)
        .all()
    )
    data = [
        {
            "id_opcion": r.id_opcion,
            "opciones_rol": r.opciones_rol
        }
        for r in resultados
    ]
    return jsonify(data)


@permisos_bp.route('/grabaropciones', methods=['POST'])
def grabaropciones():
    try:
        id_rol = request.form.get('id_rol')
        id_opciones = request.form.getlist('sel_opciones[]')

        if not id_rol:
            return jsonify({'success': False, 'mensaje': 'Falta id_rol'}), 500

        RolOpcion.query.filter_by(id_rol=id_rol).delete()
        for id_opcion in id_opciones:
            nueva = RolOpcion(id_rol=id_rol, id_opcion=id_opcion)
            db.session.add(nueva)

        db.session.commit()
        return jsonify({'success': True, 'mensaje': 'Opciones actualizadas correctamente'})

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({'success': False, 'mensaje': 'Error en actualización id_rol', 'error': str(e)}), 500
    
@permisos_bp.route('/api/menus', methods=['GET'])
def obtenermenus():
    stmt = (
        db.session.query(
            Menu.id_menu,
            Menu.nombre_menu,
            Menu.icono_menu
        )
        .order_by(Menu.id_menu)
    )
    results = db.session.execute(stmt).mappings().all()
    data = []
    for row in results:
        d = dict(row)
        if not d["icono_menu"]:
            d["icono_menu"] = "default-icon.svg"
        data.append(d)

    return jsonify(data)


# --- Mostrar la página de opciones ---
@permisos_bp.route('/opciones')
@login_required
def opciones():
    return render_template('permisos/opciones.html', user=current_user, page_title="Listado de Opciones")
    
@permisos_bp.route('/api/opciones/<int:id_opcion>', methods=['GET'])
def obtener_opciones(id_opcion):
    try:
        stmt = (
            db.session.query(
                Opcion.id_opcion,
                Opcion.nombre_opcion,
                Opcion.ruta_opcion,
                Opcion.activo,
                Opcion.id_menu,
                Menu.nombre_menu
            )
            .outerjoin(Menu, Opcion.id_menu == Menu.id_menu)
        )
        if id_opcion > 1:
            stmt = stmt.filter(Opcion.id_opcion == id_opcion)
            
            
        stmt = stmt.order_by(Opcion.id_opcion)
      
        results = db.session.execute(stmt).mappings().all()
        data = []
        for row in results:
            d = dict(row)
            d["activo_texto"] = "Activo" if d["activo"] else "Inactivo"
            data.append(d)
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@permisos_bp.route('/grabaropcion', methods=['POST'])
def grabaropcion():
    try:
        id_opcion = request.form.get('id_opcion')
        nombre_opcion = request.form.get('nombre_opcion')
        ruta_opcion = request.form.get('ruta_opcion')
        activo = request.form.get('activo') == 'true'

        # <<< NUEVO >>>
        id_menu = request.form.get('id_menu')
        icono_opcion = request.form.get('icono_opcion') or "svg-icon"

        if not nombre_opcion or not ruta_opcion or not id_menu:
            return jsonify({"success": False, "message": "Todos los campos son requeridos"}), 400

        if not id_opcion:
            nueva_opcion = Opcion(
                nombre_opcion=nombre_opcion,
                ruta_opcion=ruta_opcion,
                activo=activo,
                id_menu=id_menu,               # <<< NUEVO >>>
                icono_opcion=icono_opcion      # <<< NUEVO >>>
            )
            db.session.add(nueva_opcion)
            mensaje = "Opción creada correctamente"
        else:
            opcion = Opcion.query.get(id_opcion)
            if not opcion:
                return jsonify({"success": False, "message": "Opción no encontrada"}), 404

            opcion.nombre_opcion = nombre_opcion
            opcion.ruta_opcion = ruta_opcion
            opcion.activo = activo
            opcion.id_menu = id_menu              # <<< NUEVO >>>
            opcion.icono_opcion = icono_opcion    # <<< NUEVO >>>

            mensaje = "Opción actualizada correctamente"

        db.session.commit()
        return jsonify({"success": True, "message": mensaje})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

    

    






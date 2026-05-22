from . import dashboard_bp
from flask import render_template, jsonify
from flask_login import login_required, current_user
from collections import defaultdict
from app.models import RolOpcion, Opcion, Menu
from app.models import RedEssalud
from app.models import IpressEssalud
from app import db
from flask_mail import Message
from app import mail 

# Ruta principal del dashboard (home)
@dashboard_bp.route("/home")
@login_required
def home():
    return render_template("dashboard/home.html", user=current_user, page_title="Bienvenido")

#----------------------------------------------------------------------
# Dashboard para el usuario Red, con las estadisticas filtradas
#---------------------------------------------------------------------
@dashboard_bp.route("/vistared")
@login_required
def vistared():
    return render_template("dashboard/dashboard_red.html", user=current_user, page_title="Seguimiento RED - Resultado de Puntajes")

#----------------------------------------------------------------------
# Dashboard para el usuario Gamcc con las estadisticas filtradas
#---------------------------------------------------------------------
@dashboard_bp.route("/vistagamcc")
@login_required
def vistagamcc():
    return render_template("dashboard/dashboard_gamcc.html", user=current_user, page_title="Seguimiento GAMCC - Resultado de Puntajes")


@dashboard_bp.route("/home3")
@login_required
def home3():
    return render_template("dashboard/home3.html", user=current_user, page_title="Breadcrum home3")

#API simulada: Tipos de documento
@dashboard_bp.route("/tipos-documento", methods=["GET"])
def tiposdocumento():
    data = [
        {"id": 1, "nombre": "DNI"},
        {"id": 2, "nombre": "Carnet de Extranjería"},
        {"id": 3, "nombre": "Pasaporte"}
    ]
    return jsonify(data)

@dashboard_bp.context_processor
def inject_menu():
    print("current_usuario:", current_user)
    if not current_user.is_authenticated:
        return dict(menu_dict={})  # si no está logueado, no hay menú
    id_rol = current_user.roles_asociados[0].id_rol    
    filas = (
        db.session.query(
            Menu.nombre_menu,
            Menu.icono_menu,
            Opcion.nombre_opcion,
            Opcion.ruta_opcion
        )
        .select_from(RolOpcion)
        .join(Opcion, RolOpcion.id_opcion == Opcion.id_opcion)
        .join(Menu, Opcion.id_menu == Menu.id_menu)
        .filter(RolOpcion.id_rol == id_rol, Opcion.activo == 1)
        .order_by(Menu.id_menu)
        .all()
    )
    menu_dict = defaultdict(list)
    for nombre_menu, icono_menu, nombre_opcion, ruta_opcion in filas:        
        resultado = nombre_menu + "#" + icono_menu
        menu_dict[resultado].append(
            {"opcion": nombre_opcion, "ruta": ruta_opcion}
        )
    return dict(menu_dict=menu_dict)

@dashboard_bp.route("/enviar")
@login_required
def enviar_correo():
    msg = Message(
        subject='Prueba desde Flask con Outlook',
        recipients=['destinatario@correo.com'],
        body='¡Hola! Este es un correo de prueba enviado con Outlook.'
        # html='<b>Hola!</b> Este es un correo de prueba con HTML.'
    )
    mail.send(msg)
    return "Correo enviado correctamente"


@dashboard_bp.route('/api/redes', methods=['GET'])
def get_redes():
    try:
        redes = RedEssalud.query.order_by(RedEssalud.nombre_red).all()
        redes_data = [
            {"id_red": r.id_red, "nombre_red": r.nombre_red}
            for r in redes
        ]
        return jsonify(redes_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/api/ipress', methods=['GET'])
def get_ipress():
    try:
        ipress = IpressEssalud.query.all()
        ipress_data = [
            {"id_ipress": r.id_ipress, "nombre_ipress": r.nombre_ipress}
            for r in ipress
        ]
        return jsonify(ipress_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
import os
import secrets
from . import acredita_bp
from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from collections import defaultdict
from werkzeug.utils import secure_filename
from app.models import TecnicaEvaluacion, CondicionCriterio, Fuente, ProcesoInstitucional
from app.models import Macroproceso, Estandar, Criterio
from app import db
from app.constants import ROLES
from app.constants import ROLES_NAME
from sqlalchemy import func, cast, String
from .services import AcreditaService

# --- Página principal ---
@acredita_bp.route("/fuentes/actualizar", methods=["GET"])
@login_required
def actualizar_fuentes():
    return render_template("administrarfuentes.html",lista_roles=ROLES,nombre_roles=ROLES_NAME,user=current_user,page_title="Actualizar Fuentes Auditables")

# --- API listar macroprocesos ---
@acredita_bp.route("/api/macroprocesos", methods=["GET"])
def api_macroprocesos():
    data = (
        db.session.query(
            Macroproceso.id_macroproceso,
            Macroproceso.codigo_macroproceso,
            Macroproceso.nombre_macroproceso
        )
        .order_by(Macroproceso.nombre_macroproceso)
        .all()
    )

    return jsonify([
        {
            "id_macroproceso": m.id_macroproceso,
            "codigo": m.codigo_macroproceso,
            "nombre": m.nombre_macroproceso
        }
        for m in data
    ])

# --- API listar estándares por macroproceso ---
@acredita_bp.route("/api/estandares/<int:id_macroproceso>", methods=["GET"])
def api_estandares(id_macroproceso):
    data = (
        db.session.query(
            Estandar.id_estandar,
            Estandar.codigo_estandar,
            Estandar.nombre_estandar
        )
        .filter(Estandar.id_macroproceso == id_macroproceso)
        .order_by(Estandar.codigo_estandar)
        .all()
    )

    return jsonify([
        {
            "id_estandar": e.id_estandar,
            "codigo": e.codigo_estandar,
            "nombre": e.nombre_estandar
        }
        for e in data
    ])

# --- API listar criterios por estándar ---
@acredita_bp.route("/api/criterios/<int:id_estandar>", methods=["GET"])
def api_criterios(id_estandar):
    data = (
        db.session.query(
            Criterio.id_criterio,
            Criterio.codigo_criterio,
            Criterio.nombre_criterio
        )
        .filter(Criterio.id_estandar == id_estandar)
        .order_by(Criterio.codigo_criterio)
        .all()
    )

    return jsonify([
        {
            "id_criterio": c.id_criterio,
            "codigo": c.codigo_criterio,
            "nombre": c.nombre_criterio
        }
        for c in data
    ])

# --- API LISTA COMBINADA PARA LA TABLA ---
@acredita_bp.route("/api/combinado", methods=["GET"])
def api_combinado():
    id_macro = request.args.get("id_macroproceso")
    id_estandar = request.args.get("id_estandar")
    id_criterio = request.args.get("id_criterio")

    query = (
        db.session.query(
            Macroproceso.codigo_macroproceso,
            Macroproceso.nombre_macroproceso,
            Estandar.codigo_estandar,
            Estandar.nombre_estandar,
            Criterio.codigo_criterio,
            Criterio.nombre_criterio,
            Criterio.id_criterio
        )
        .join(Estandar, Estandar.id_macroproceso == Macroproceso.id_macroproceso)
        .join(Criterio, Criterio.id_estandar == Estandar.id_estandar)
    )

    if id_macro not in ["", None, "0"]:
        query = query.filter(Macroproceso.id_macroproceso == id_macro)

    if id_estandar not in ["", None, "0"]:
        query = query.filter(Estandar.id_estandar == id_estandar)

    if id_criterio not in ["", None, "0"]:
        query = query.filter(Criterio.id_criterio == id_criterio)

    rows = query.all()

    return jsonify([
        {
            "macro": f"{r.codigo_macroproceso} {r.nombre_macroproceso}",
            "estandar": f"{r.codigo_estandar}  {r.nombre_estandar}",
            "criterio": f"{r.codigo_criterio}  {r.nombre_criterio}",
            "id_criterio": f"{r.id_criterio}"
        }
        for r in rows
    ])

# --- Página administrar condiciones  ---
@acredita_bp.route("/condicion/actualizar", methods=["POST"])
@login_required
def actualizar_condiciones():
    id_criterio = request.form.get("id_criterio")
    nombre_criterio = request.form.get("nombre_criterio")
    return render_template("condiciones.html",lista_roles=ROLES,nombre_roles=ROLES_NAME,user=current_user,id_criterio=id_criterio,nombre_criterio=nombre_criterio,page_title="Actualizar Condiciones y Fuentes")

@acredita_bp.route("/api/condiciones/<int:id>", methods=["GET"])
def ver_condiciones(id):
    stmt = (
        db.session.query(
            CondicionCriterio.id_condicion,
            CondicionCriterio.nombre_condicion,
            CondicionCriterio.id_tecnica,
            TecnicaEvaluacion.nombre_tecnica,
            CondicionCriterio.puntaje_condicion,
            Fuente.id_fuente,
            Fuente.nombre_fuente,
            Fuente.link_fuente
        )
        .outerjoin(Fuente, Fuente.id_condicion == CondicionCriterio.id_condicion)
        .outerjoin(TecnicaEvaluacion, TecnicaEvaluacion.id_tecnica == CondicionCriterio.id_tecnica)
        .where(CondicionCriterio.id_criterio == id)
    )
    resultados = db.session.execute(stmt).all()
    condiciones_dict = {}

    for r in resultados:
        id_cond = r.id_condicion

        # Si aún no existe la condición en el diccionario, la creamos
        if id_cond not in condiciones_dict:
            condiciones_dict[id_cond] = {
                "id_condicion": r.id_condicion,
                "nombre_condicion": r.nombre_condicion,
                "id_tecnica": r.id_tecnica,
                "nombre_tecnica": r.nombre_tecnica,
                "puntaje_condicion": r.puntaje_condicion,
                "fuentes": []  # aquí se irán acumulando las fuentes
            }

        # Agregamos la fuente solo si existe (por el LEFT JOIN puede venir None)
        if r.id_fuente is not None:
            condiciones_dict[id_cond]["fuentes"].append({
                "id_fuente": r.id_fuente,
                "nombre_fuente": r.nombre_fuente,
                "link_fuente": r.link_fuente
            })

    # Convertimos el dict (clave = id_condicion) en lista
    data = list(condiciones_dict.values())

    return jsonify(data)

# --- API tecnicas ---
@acredita_bp.route("/api/tecnicas", methods=["GET"])
def api_tecnicas():
    data = (
        db.session.query(
            TecnicaEvaluacion.id_tecnica,
            TecnicaEvaluacion.nombre_tecnica
        )
        .all()
    )

    return jsonify([
        {
            "id_tecnica": m.id_tecnica,
            "nombre": m.nombre_tecnica
        }
        for m in data
    ])
        
@acredita_bp.route('/condicion', methods=['POST'])
def crear_condicion():
    data = request.form
    resultado = AcreditaService.crear_condicion(data)
    return jsonify(resultado), 200 if resultado['success'] else 400

@acredita_bp.route('/condicion/<int:id_condicion>', methods=['PUT'])
def actualizar_condicion(id_condicion):
    data = request.form
    resultado = AcreditaService.actualizar_condicion(id_condicion,data)
    return jsonify(resultado), 200 if resultado['success'] else 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf'}
                  
@acredita_bp.route('/uploadfile', methods=["GET","POST"])
def uploadregistro():
    msg = ''
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

@acredita_bp.route("/api/condicion/<int:id>", methods=["GET"])
def get_condicion(id):
    condicion = AcreditaService.get_condicion_by_id(id)
    if not condicion:
        return jsonify({"error": "Condición no encontrada"}), 404
    return jsonify(condicion), 200

@acredita_bp.route("/api/fuentes/<int:id_condicion>")
def get_fuentes(id_condicion):
    fuentes = Fuente.query.filter_by(id_condicion=id_condicion).all()
    data = [
        {
            "id_fuente": f.id_fuente,
            "nombre_fuente": f.nombre_fuente,
            "link_fuente": f.link_fuente
        }
        for f in fuentes
    ]
    return jsonify(data)

@acredita_bp.route('/grabarfuentes', methods=['POST'])
def grabarfuentes():

    try:
        data = request.get_json()
        # Validar lista
        if not isinstance(data, list):
            return jsonify({"success": False, "mensaje": "JSON debe ser una lista"}), 400

        for item in data:
            id_fuente = item.get("id_fuente")
            nombre = item.get("nombre_fuente")
            link = item.get("link_fuente")
            id_condicion = item.get("id_condicion")

            if not id_fuente:
                nueva = Fuente(
                    nombre_fuente=nombre,
                    link_fuente=link,
                    id_condicion=id_condicion
                )
                db.session.add(nueva)
                mensaje = 'Fuente registrada correctamente'

            else:
                fuente = Fuente.query.get(id_fuente)
                if fuente:
                    fuente.nombre_fuente = nombre
                    fuente.link_fuente = link
                    mensaje = 'Fuente actualizada correctamente'

        db.session.commit()
        return jsonify({'success': True, 'mensaje': mensaje})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'mensaje': e})
    
@acredita_bp.route('/procesosinstitucionales', methods=['GET'])
def listar_procesos():
    response = AcreditaService.listar_procesos()
    return jsonify(response), 200

@acredita_bp.route('/criterio/<int:id_criterio>', methods=['GET'])
def obtener_criterio(id_criterio):
    response = AcreditaService.obtener_criterio(id_criterio)
    if not response:
        return jsonify({
            "success": False,
            "message": "Criterio no encontrado"
        }), 404

    return jsonify(response), 200
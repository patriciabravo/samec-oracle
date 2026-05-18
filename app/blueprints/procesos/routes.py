import os
import secrets
import app.constants as constants
from . import procesos_bp
from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from collections import defaultdict
from werkzeug.utils import secure_filename
from app.models import TecnicaEvaluacion, CondicionCriterio, Fuente, ProcesoInstitucional,TipoReporte,Autoevaluacion
from app.models import Macroproceso, Estandar, Criterio, IpressEssalud,AutoevaluacionReporte, AutoevaluacionReporteComentario, TipoObservacion
from app import constants, db
from flask import send_from_directory
import hashlib
import time
import shutil
import traceback
from sqlalchemy.orm import aliased
from sqlalchemy import case, func, text, Integer, and_, cast, case, or_
from sqlalchemy.exc import IntegrityError


# ------------------------------
# Listado de Procesos Institucionales
# ------------------------------
@procesos_bp.route("/reportar")
@login_required
def procesos():
    IdIpress = getattr(current_user, "id_ipress", None)
    id_anio_acreditacion = constants.ACREDITACION_ACTUAL
    id_evaluacion = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.id_ipress == IdIpress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .scalar()
    )
    print('id evaluation ',id_evaluacion)
    return render_template("reportar.html", user=current_user, id_autoevaluacion=id_evaluacion, page_title='Reporte por Procesos Institucionales')


# ------------------------------------------------------
# API 1 - Datatable de Procesos Institucionales
# ------------------------------------------------------
@procesos_bp.route("/api/process", methods=["GET"])
def api_procesos():

    IdIpress = getattr(current_user, "id_ipress", None)
    id_anio_acreditacion = constants.ACREDITACION_ACTUAL
    
    ipress = db.session.query(IpressEssalud).filter_by(id_ipress=IdIpress).first()
    nivel_ipress_usuario = getattr(ipress, "nivel_ipress", None)
    
    
    MAPA_NIVEL = {
        "I-1": Criterio.nivel_i_1,
        "I-2": Criterio.nivel_i_2,
        "I-3": Criterio.nivel_i_3,
        "I-4": Criterio.nivel_i_4,
        "II-1": Criterio.nivel_ii_1,
        "II-2": Criterio.nivel_ii_2,        
        "III-1": Criterio.nivel_iii_1
    }
    columna_comparar = MAPA_NIVEL.get(nivel_ipress_usuario)

    #autoevaluación activa
    id_autoevaluacion = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.id_ipress == IdIpress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .scalar()
    )
    print('id_ae',id_autoevaluacion)

    #reemplazar luego el nivel
    query = (
        db.session.query(
            ProcesoInstitucional.id_proceso,
            ProcesoInstitucional.nombre_proceso,
            case(
                (
                    and_(
                        or_(Fuente.link_fuente.is_(None), Fuente.link_fuente == ''),
                        or_(AutoevaluacionReporte.link_reporte.is_(None), AutoevaluacionReporte.link_reporte == ''),
                        or_(AutoevaluacionReporte.ruta_archivo.is_(None), AutoevaluacionReporte.ruta_archivo == '')
                    ),
                    0
                ),
                else_=1).label("totales"),
            AutoevaluacionReporteComentario.es_observado
        )
        .select_from(Fuente)
        .outerjoin(
            CondicionCriterio,
            Fuente.id_condicion == CondicionCriterio.id_condicion
        )
        .outerjoin(
            Criterio,
            Criterio.id_criterio == CondicionCriterio.id_criterio
        )
        .outerjoin(
            ProcesoInstitucional,
            ProcesoInstitucional.id_proceso == Criterio.id_proceso
        )
        .outerjoin(
            AutoevaluacionReporte,
            and_(AutoevaluacionReporte.id_fuente == Fuente.id_fuente,AutoevaluacionReporte.id_autoevaluacion == id_autoevaluacion
            )
        )
        .outerjoin(
            AutoevaluacionReporteComentario,
            and_(AutoevaluacionReporteComentario.id_fuente == Fuente.id_fuente,AutoevaluacionReporteComentario.id_autoevaluacion == id_autoevaluacion
            )
        )
        .filter(
            CondicionCriterio.id_tecnica == 4,
            columna_comparar == 1,
            ProcesoInstitucional.id_proceso != 0
        )
        .order_by(ProcesoInstitucional.id_proceso)
    )
    rows = query.all()

    print(
        query.statement.compile(
            compile_kwargs={"literal_binds": True}
        )
    )
    
    resultado = {}
    for row in rows:
        id_proceso = row.id_proceso
        nombre = row.nombre_proceso
        valor1 = row.totales or 0
        tiene_obs = row.es_observado


        grupo = resultado.setdefault(id_proceso, {
            "id_proceso": id_proceso,
            "nombre_proceso": nombre,
            "cantidad_reportes": 0,
            "cantidad_filas": 0,
            "cantidad_observaciones": 0
        })

        grupo["cantidad_reportes"] += valor1
        grupo["cantidad_filas"] += 1
        if tiene_obs == 0:
            grupo["cantidad_observaciones"] += 1
    
    # Convertir a lista (sin id_proceso)
    json_data = list(resultado.values())
    
    
    for item in json_data:
        if item["cantidad_filas"] > 0:
            division = item["cantidad_reportes"] / item["cantidad_filas"]
        else:
            division = 0

        if division == 0:
            item["estado"] = "pendiente"
        elif division == 1:
            item["estado"] = "completado"
        else:
            item["estado"] = "en proceso"
        
    return jsonify({
            "id_autoevaluacion": id_autoevaluacion,
            "procesos": json_data           
    })




# ------------------------------
# Listado de Fuentes de acuerdo al proceso
# ------------------------------

@procesos_bp.route("/evaluado/<int:id_proceso>/fuentes",methods=["POST"])
@login_required
def pagina_fuentes(id_proceso):

    # Obtener nombre del proceso
    proc = ProcesoInstitucional.query.filter_by(id_proceso=id_proceso).first()
    nombre_proceso = proc.nombre_proceso if proc else "Proceso desconocido"

    # Consulta de fuentes (MISMA QUE LA API)
    query = (
        db.session.query(
            Fuente.id_fuente,
            Fuente.nombre_fuente,
            Fuente.link_fuente
        )
        .select_from(Fuente)
        .outerjoin(CondicionCriterio, CondicionCriterio.id_condicion == Fuente.id_condicion)
        .outerjoin(Criterio, Criterio.id_criterio == CondicionCriterio.id_criterio)
        .outerjoin(ProcesoInstitucional, ProcesoInstitucional.id_proceso == Criterio.id_proceso)
        .filter(ProcesoInstitucional.id_proceso == id_proceso)
        .order_by(Fuente.nombre_fuente)   
    )
    result = db.session.execute(query, {"id_proceso": id_proceso}).fetchall()

    data = [
        {
            "id_fuente": row.id_fuente,
            "nombre_fuente": row.nombre_fuente,
            "link_fuente": row.link_fuente
        }
        for row in result
    ]

    return render_template(
        "process_fuente.html",
        page_title='Reporte de Fuentes',
        id_proceso=id_proceso,
        nombre_proceso=nombre_proceso,
        data=data 
    )


def get_uploads_base():
    """
    Retorna la ruta absoluta a la carpeta /uploads
    (ubicada fuera de app)
    """
    return os.path.abspath(
        os.path.join(current_app.root_path, "..", "uploads")
    )



# ---------------------------------------------------------
# API 2 - FUENTES agrupadas por técnica para un proceso
# ---------------------------------------------------------
@procesos_bp.route("/api/process/<int:id_proceso>/fuentes", methods=["GET"])
def api_fuentes_proceso(id_proceso):

    id_ipress = getattr(current_user, "id_ipress", None)
    print("ipresss->",id_ipress)
    if not id_ipress:
        return jsonify({"error": id_ipress, "proceso": "", "fuentes": []})

    # ===============================
    # AUTOEVALUACIÓN ACTIVA
    # ===============================
    id_anio_acreditacion = constants.ACREDITACION_ACTUAL
    resultado = (
        db.session.query(
            Autoevaluacion.id_autoevaluacion,
            Autoevaluacion.estado
        )
        .filter(Autoevaluacion.id_ipress == id_ipress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .first()
    )
    if resultado:
        id_autoevaluacion = resultado.id_autoevaluacion
        estado_autoevaluacion = resultado.estado
    else:
        id_autoevaluacion = None
        estado_autoevaluacion = None

    if estado_autoevaluacion == constants.ESTADO_ACREDITACION_ACTIVO:
        permiso = 'edit'
    else:
        permiso = 'view'


    ipress = db.session.query(IpressEssalud).filter_by(id_ipress=id_ipress).first()
    nivel_ipress_usuario = getattr(ipress, "nivel_ipress", None)

    proceso = ProcesoInstitucional.query.filter_by(id_proceso=id_proceso).first()
    nombre_proceso = proceso.nombre_proceso if proceso else ""

    # ===============================
    # ALIASES
    # ===============================
    AutoevalReporte = aliased(AutoevaluacionReporte)
    Comentario = aliased(AutoevaluacionReporteComentario)

    # ===============================
    # QUERY PRINCIPAL
    # ===============================
    MAPA_NIVEL = {
        "I-1": Criterio.nivel_i_1,
        "I-2": Criterio.nivel_i_2,
        "I-3": Criterio.nivel_i_3,
        "I-4": Criterio.nivel_i_4,
        "II-1": Criterio.nivel_ii_1,
        "II-2": Criterio.nivel_ii_2,        
        "III-1": Criterio.nivel_iii_1
    }
    columna_comparar = MAPA_NIVEL.get(nivel_ipress_usuario)
        
    query = (
        db.session.query(
            Fuente.id_fuente,
            Fuente.nombre_fuente,
            Fuente.link_fuente,
            CondicionCriterio.nombre_condicion,
            Criterio.id_criterio,
            Criterio.codigo_criterio,      #  CLAVE
            Criterio.nombre_criterio,
            AutoevalReporte.nombre_archivo,
            AutoevalReporte.ruta_archivo,
            AutoevalReporte.link_reporte,
            Comentario.es_observado,
            Comentario.observacion_fuente,
            TipoObservacion.nombre_tipo_observacion
        )
        .select_from(Fuente)
        .outerjoin(AutoevalReporte,(AutoevalReporte.id_fuente == Fuente.id_fuente) & (AutoevalReporte.id_autoevaluacion == id_autoevaluacion))
        .outerjoin(Comentario,(Comentario.id_fuente == Fuente.id_fuente) & (Comentario.id_autoevaluacion == id_autoevaluacion))
        .outerjoin(TipoObservacion, TipoObservacion.id_tipo_observacion == Comentario.observacion_fuente)
        .outerjoin(CondicionCriterio, CondicionCriterio.id_condicion == Fuente.id_condicion)
        .outerjoin(Criterio, Criterio.id_criterio == CondicionCriterio.id_criterio)
        .outerjoin(ProcesoInstitucional, ProcesoInstitucional.id_proceso == Criterio.id_proceso)
        .filter(ProcesoInstitucional.id_proceso == id_proceso)
        .filter(CondicionCriterio.id_tecnica == 4)
        .filter(Criterio.aplica_essalud == 1)
        .filter(columna_comparar == 1)
        
        .order_by(Criterio.codigo_criterio)
    )

    print(
    query.statement.compile(
        compile_kwargs={"literal_binds": True}
    )
    )
    rows = query.all()

    fuentes = []
    for r in rows:
        fuentes.append({
            "id_fuente": r.id_fuente,
            "nombre_fuente": r.nombre_fuente,
            "link_fuente": r.link_fuente,
            "nombre_condicion": r.nombre_condicion,
            "id_criterio": r.id_criterio,
            "codigo_criterio": r.codigo_criterio,   #  HIDDEN
            "nombre_criterio": r.nombre_criterio,
            "nombre_archivo": r.nombre_archivo,
            "ruta_archivo": r.ruta_archivo,
            "link_reporte": r.link_reporte,
            "es_observado": r.es_observado,
            "observacion_fuente": r.nombre_tipo_observacion,
            "permiso":permiso
        })

    return jsonify({
        "error": "",
        "proceso": nombre_proceso,
        "fuentes": fuentes
    })

    


@procesos_bp.route("/api/fuente/<int:id_fuente>/temp", methods=["POST"])
def upload_temp_fuente(id_fuente):

    # 1. Validar archivo
    if "file" not in request.files:
        return jsonify({"error": "No se envió archivo"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nombre vacío"}), 400

    allowed = {"pdf", "docx", "xlsx", "xls"}
    ext = file.filename.rsplit(".", 1)[1].lower()

    if ext not in allowed:
        return jsonify({"error": "Tipo no permitido"}), 400

    # 2. Nombre original
    nombre_real = secure_filename(file.filename)

    # 3. Generar hash único EXACTO como ya tenías
    timestamp = str(time.time()).encode()
    nombre_hash = hashlib.sha256(timestamp).hexdigest()[:20]
    nombre_hash = f"{nombre_hash}.{ext}"

    # 4. Guardar archivo en carpeta temporal
    base_uploads = get_uploads_base()
    temp_folder = os.path.join(base_uploads, "temp_fuentes")
    os.makedirs(temp_folder, exist_ok=True)

    save_path = os.path.join(temp_folder, nombre_hash)
    file.save(save_path)

    # 5. Devolver referencias temporales
    return jsonify({
        "message": "Archivo subido temporalmente",
        "nombre_archivo": nombre_real,
        "nombre_temp": nombre_hash
    })


@procesos_bp.route("/api/fuente/<int:id_fuente>/upload", methods=["POST"])
@login_required
def upload_fuente(id_fuente):
    try:
        data = request.get_json(silent=True) or {}
        nombre_temp = data.get("nombre_temp")
        nombre_real = data.get("nombre_real") or nombre_temp or "documento"

        if not nombre_temp:
            return jsonify({"error": "No se recibió archivo temporal"}), 400

        # ======================================
        # 1️⃣ OBTENER AUTOEVALUACIÓN ACTIVA ( CLAVE)
        # ======================================
        id_ipress = getattr(current_user, "id_ipress", None)
        id_anio = constants.ACREDITACION_ACTUAL

        id_autoevaluacion = (
            db.session.query(Autoevaluacion.id_autoevaluacion)
            .filter(Autoevaluacion.id_ipress == id_ipress)
            .filter(Autoevaluacion.periodo == id_anio)
            .scalar()
        )

        if not id_autoevaluacion:
            return jsonify({"error": "No existe autoevaluación activa"}), 400

        # ======================================
        # 2️⃣ MOVER ARCHIVO DE TEMP → FINAL
        # ======================================
        base_uploads = get_uploads_base()
        temp_folder = os.path.join(base_uploads, "temp_fuentes")
        final_folder = os.path.join(base_uploads, "fuentes")
        os.makedirs(final_folder, exist_ok=True)

        origen = os.path.join(temp_folder, nombre_temp)
        destino = os.path.join(final_folder, nombre_temp)

        if os.path.exists(origen):
            shutil.move(origen, destino)
        elif not os.path.exists(destino):
            # Ya no está en temp ni en fuentes: posible doble clic o sesión distinta
            return jsonify({"error": "Archivo temporal no existe. Sube de nuevo el archivo con «Subir» y luego Guardar."}), 400
        # Si destino ya existe (archivo ya movido antes), solo actualizamos BD más abajo (idempotente)

        # ======================================
        # 3️⃣ DATOS DE FUENTE / CONDICIÓN / CRITERIO
        # ======================================
        fuente = Fuente.query.filter_by(id_fuente=id_fuente).first()
        if not fuente:
            return jsonify({"error": "No existe la fuente"}), 400

        id_condicion = fuente.id_condicion
        condicion = CondicionCriterio.query.filter_by(id_condicion=id_condicion).first()
        if not condicion:
            return jsonify({"error": "No se encontró la condición asociada a la fuente"}), 400
        id_criterio = condicion.id_criterio

        # ======================================
        # 4️⃣ INSERT O UPDATE (NO DUPLICA)
        # ======================================
        tipo_archivo = TipoReporte.query.filter_by(id_tiporeporte=1).first()
        if not tipo_archivo:
            return jsonify({
                "error": "Falta configurar tipo de reporte en la base de datos. Ejecute: INSERT INTO tipo_reporte (id_tiporeporte, nombre_tiporeporte) VALUES (1, 'Archivo'), (2, 'Link');"
            }), 500

        reporte = AutoevaluacionReporte.query.filter_by(
            id_autoevaluacion=id_autoevaluacion,
            id_fuente=id_fuente
        ).first()

        if not reporte:
            reporte = AutoevaluacionReporte(
                id_autoevaluacion=id_autoevaluacion,
                id_fuente=id_fuente,
                id_condicion=id_condicion,
                id_criterio=id_criterio,
                id_tiporeporte=1,
                nombre_archivo=nombre_real,
                ruta_archivo=nombre_temp,
                link_reporte=None
            )
            db.session.add(reporte)
        else:
            reporte.id_tiporeporte = 1
            reporte.nombre_archivo = nombre_real
            reporte.ruta_archivo = nombre_temp
            reporte.link_reporte = None
            reporte.id_condicion = id_condicion
            reporte.id_criterio = id_criterio

        db.session.commit()

        return jsonify({
            "message": "Archivo guardado correctamente",
            "ruta_archivo": nombre_temp,
            "nombre_archivo": nombre_real
        })
    except IntegrityError as e:
        db.session.rollback()
        err_msg = str(e.orig) if getattr(e, "orig", None) else str(e)
        if "tipo_reporte" in err_msg or "id_tiporeporte" in err_msg:
            return jsonify({"error": "Falta configurar tipo de reporte (archivo) en la base de datos. Inserte un registro en tipo_reporte con id_tiporeporte=1."}), 500
        return jsonify({"error": f"Error de integridad en base de datos: {err_msg}"}), 500
    except Exception as e:
        db.session.rollback()
        try:
            current_app.logger.exception("Error en upload_fuente")
        except Exception:
            traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@procesos_bp.route("/api/fuente/<int:id_fuente>/link", methods=["POST"])
@login_required
def guardar_link_fuente(id_fuente):

    data = request.get_json()
    link = data.get("link")

    if not link:
        return jsonify({"error": "Link vacío"}), 400

    # ======================================
    # 1️⃣ AUTOEVALUACIÓN ACTIVA
    # ======================================
    id_ipress = getattr(current_user, "id_ipress", None)
    id_anio = constants.ACREDITACION_ACTUAL

    id_autoevaluacion = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.id_ipress == id_ipress)
        .filter(Autoevaluacion.periodo == id_anio)
        .scalar()
    )

    if not id_autoevaluacion:
        return jsonify({"error": "No existe autoevaluación activa"}), 400

    # ======================================
    # 2️⃣ FUENTE / CONDICIÓN / CRITERIO
    # ======================================
    fuente = Fuente.query.filter_by(id_fuente=id_fuente).first()
    if not fuente:
        return jsonify({"error": "Fuente no existe"}), 400

    id_condicion = fuente.id_condicion

    condicion = CondicionCriterio.query.filter_by(id_condicion=id_condicion).first()
    id_criterio = condicion.id_criterio if condicion else None

    if not id_condicion or not id_criterio:
        return jsonify({"error": "No se pudo determinar condición o criterio"}), 400

    # ======================================
    # 3️⃣ INSERT O UPDATE (NO DUPLICA)
    # ======================================
    reporte = AutoevaluacionReporte.query.filter_by(
        id_autoevaluacion=id_autoevaluacion,
        id_fuente=id_fuente
    ).first()

    if not reporte:
        reporte = AutoevaluacionReporte(
            id_autoevaluacion=id_autoevaluacion,
            id_fuente=id_fuente,
            id_condicion=id_condicion,
            id_criterio=id_criterio,
            id_tiporeporte=2,      # LINK
            link_reporte=link,
            nombre_archivo=None,
            ruta_archivo=None
        )
        db.session.add(reporte)
    else:
        reporte.id_tiporeporte = 2
        reporte.link_reporte = link
        reporte.nombre_archivo = None
        reporte.ruta_archivo = None
        reporte.id_condicion = id_condicion
        reporte.id_criterio = id_criterio

    db.session.commit()

    return jsonify({"ok": True})

@procesos_bp.route("/uploads/fuentes/<path:filename>")
@login_required
def ver_fuente(filename):

    base_uploads = get_uploads_base()
    carpeta_fuentes = os.path.join(base_uploads, "fuentes")

    return send_from_directory(
        carpeta_fuentes,
        filename,
        as_attachment=False
    )




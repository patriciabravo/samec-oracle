from . import calculoacredita_bp
from flask import render_template, jsonify, request, send_file
from flask_login import login_required, current_user
from app.models import Macroproceso, Estandar, Criterio, AutoevaluacionReporteCriterio, Autoevaluacion, IpressEssalud
from app import db
from .services import obtener_datos_calculo
from .excel_export import generar_excel_CalculoAcredita
from app.constants import MAPA_NIVEL
from app.constants import ACREDITACION_ACTUAL


@calculoacredita_bp.route("/resultados", methods=["POST"])
@login_required
def resultados():
    id_autoevaluacion = request.form.get("id_autoevaluacion")
    id_ipress = request.form.get("id_ipress")
    return render_template(
        "calculoacredita.html",
        current_user=current_user,
        page_title="Resultados de la Autoevaluación",
        id_autoevaluacion=id_autoevaluacion,
        id_ipress=id_ipress
    )

@calculoacredita_bp.route("/calculo/id_autoevaluacion/<int:id_autoevaluacion>/id_ipress/<int:id_ipress>", methods=["GET"])
def calculo(id_autoevaluacion, id_ipress):
    datos = obtener_datos_calculo(id_autoevaluacion, id_ipress)
    if not datos:
        return jsonify({"data": [], "categorias": [], "porcentaje": 0, "tiene_datos": False, "status": "error"}), 404

    output = list(datos["result"].values())
    return jsonify({
        "data": output,
        "categorias": datos["datos_categoria"],
        "porcentaje": datos["porcentaje_final"],
        "tiene_datos": datos["tiene_datos"],
        "status": "ok"
    })


@calculoacredita_bp.route("/exportar_excel/id_autoevaluacion/<int:id_autoevaluacion>/id_ipress/<int:id_ipress>", methods=["GET"])
@login_required
def exportar_excel(id_autoevaluacion, id_ipress):
    datos = obtener_datos_calculo(id_autoevaluacion, id_ipress)
    if not datos:
        return jsonify({"error": "No se encontraron datos"}), 404
    if not datos["tiene_datos"]:
        return jsonify({"error": "No hay datos para exportar"}), 400

    buffer = generar_excel_CalculoAcredita(datos)
    ipress = datos["ipress"]
    nombre_archivo = f"CalculoAcredita_{ipress.codigo_ipress}_{ipress.nombre_ipress[:30]}.xlsx".replace(" ", "_")

    return send_file(
        buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nombre_archivo
    )

@calculoacredita_bp.route('/api/autoevaluacion/guardar_puntaje', methods=['POST'])
def guardar_puntaje_autoevaluacion():

    data = request.get_json()
    id_ipress = data.get("id_ipress")
    id_autoevaluacion = data.get("id_autoevaluacion")
    puntaje = data.get("puntaje")

    try:

        db.session.query(Autoevaluacion).filter(
            Autoevaluacion.id_ipress == id_ipress,
            Autoevaluacion.id_autoevaluacion == id_autoevaluacion
        ).update({
            "puntaje_obtenido": float(puntaje)
        })
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Puntaje guardado correctamente"
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@calculoacredita_bp.route("/api/get_porcentaje_autoevaluacion/<int:id_ipress>", methods=["GET"])
@login_required
def obtener_porcentaje_autoevaluacion(id_ipress):

    id_anio_acreditacion = ACREDITACION_ACTUAL
    id_ae = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.id_ipress == id_ipress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .scalar()
    )
    print(id_ae)
    resultado = (
        db.session.query(Autoevaluacion.puntaje_obtenido)
        .filter(Autoevaluacion.id_ipress == id_ipress)
        .filter(Autoevaluacion.id_autoevaluacion == id_ae)
        .first()
    )
    print('el porcentaje ',resultado)
    porcentaje = float(resultado[0]) if resultado and resultado[0] else 0

    return jsonify({
        "porcentaje_obtenido": porcentaje
    })
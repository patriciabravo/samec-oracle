import os
import secrets
import app.constants as constants
from . import graficos_bp
from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from collections import defaultdict
from werkzeug.utils import secure_filename
from app.models import Autoevaluacion, AutoevaluacionReporte, AutoevaluacionReporteCriterio, AutoevaluacionReporteComentario
from app.models import Macroproceso, Estandar, Criterio, IpressEssalud, RedEssalud
from app import db
from sqlalchemy import and_, func, cast, String, select, literal, func, or_
from sqlalchemy import insert

#-----------------------------------------
#Vista del Grafico de Barras po Puntaje
#----------------------------------------
@graficos_bp.route("/test")
def test():
    return render_template("estadisticaspuntajes.html", user=current_user)


#-------------------------
# API: Dame Redes
#--------------------------
@graficos_bp.route("/api/redes")
def obtener_redes():

    redes = (
        db.session.query(
            RedEssalud.id_red,
            RedEssalud.nombre_red
        )
        .order_by(RedEssalud.nombre_red)
        .all()
    )
    return jsonify([
        {
            "id_red": red.id_red,
            "nombre_red": red.nombre_red
        }
        for red in redes
    ])


#-------------------------
# API: Dame Ipress
#--------------------------
@graficos_bp.route("/api/ipress", methods=["GET"])
def obtener_ipress():

    ipress = (
        db.session.query(
            IpressEssalud.id_ipress,
            IpressEssalud.nombre_ipress
        )
        .order_by(IpressEssalud.nombre_ipress.asc())
        .all()
    )

    return jsonify([
        {
            "id_ipress": r.id_ipress,
            "nombre_ipress": r.nombre_ipress
        }
        for r in ipress
    ])


#-------------------------
# API: Dame Ipress por Red
#--------------------------
@graficos_bp.route("/api/ipress_por_red/<int:id_red>")
def ipress_por_red(id_red):   

    if not id_red:
        return jsonify([])

    ipress = (
        db.session.query(IpressEssalud.id_ipress,
                         IpressEssalud.nombre_ipress)
        .filter(IpressEssalud.id_red == id_red)
        .order_by(IpressEssalud.nombre_ipress)
        .all()
    )

    return jsonify([
        {
            "id_ipress": ip.id_ipress,
            "nombre_ipress": ip.nombre_ipress
        }
        for ip in ipress
    ])

#-------------------------
# API: Dame Macroprocesos
#--------------------------
@graficos_bp.route("/api/macroprocesos", methods=["GET"])
def obtener_macroprocesos():

    macroprocesos = (
        db.session.query(
            Macroproceso.id_macroproceso,
            Macroproceso.codigo_macroproceso,
            Macroproceso.nombre_macroproceso
        )
        .order_by(Macroproceso.nombre_macroproceso.asc())
        .all()
    )

    return jsonify([
        {
            "id_macroproceso": r.id_macroproceso,
             "nombre_macroproceso": f"{r.codigo_macroproceso} - {r.nombre_macroproceso}"
        }
        for r in macroprocesos
    ])
#----------------------------------
# API: Dame Ids de Autoevaluacion
#----------------------------------
@graficos_bp.route("/api/autoevaluacion/id_ipress/<id_ipress>", methods=["GET"])
def obtener_autoevaluacion(id_ipress):

    query = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.periodo == constants.ACREDITACION_ACTUAL)
        .filter(Autoevaluacion.id_ipress == id_ipress)
    )

    resultados = query.all()

    return jsonify([r.id_autoevaluacion for r in resultados])


#-----------------------------------------------------
# FX: Recibe los ID´s de AE y suma los puntajes 0,1,2
#----------------------------------------------------

def obtener_puntajes(ids_autoevaluacion):
    query = (
        db.session.query(
            Macroproceso.codigo_macroproceso,
            Macroproceso.nombre_macroproceso,
            AutoevaluacionReporteCriterio.puntaje_criterio,
            func.count(
                AutoevaluacionReporteCriterio.puntaje_criterio
            ).label("cantidad_puntaje")
        )
        .select_from(Criterio)
        .outerjoin(
            Estandar,
            Criterio.id_estandar == Estandar.id_estandar
        )
        .outerjoin(
            Macroproceso,
            Macroproceso.id_macroproceso == Estandar.id_macroproceso
        )
        .outerjoin(
            AutoevaluacionReporteCriterio,
            Criterio.id_criterio == AutoevaluacionReporteCriterio.id_criterio
        )
        .filter(
            AutoevaluacionReporteCriterio.id_autoevaluacion.in_(ids_autoevaluacion)
        )
        .group_by(
            Macroproceso.codigo_macroproceso,
            Macroproceso.nombre_macroproceso,
            AutoevaluacionReporteCriterio.puntaje_criterio
        )
        .order_by(
            Macroproceso.codigo_macroproceso
        )
    )
    
    print(query.statement.compile(compile_kwargs={"literal_binds": True}))
    return query.all()

#-----------------------------------------------------
# API: Devuelve resultados para el grafico de puntajes
#----------------------------------------------------
@graficos_bp.route("/api/puntajes_macroproceso")
def puntajes_por_macroproceso():
    
    ids_string = request.args.get("ids", "")
    
    if ids_string:
        ids = [int(x) for x in ids_string.split(",")]
    else:
        ids = []

    print(ids)

    result = obtener_puntajes(ids)

    data_dict = {}

    for codigo, nombre, puntaje, cantidad in result:

        if nombre not in data_dict:
            data_dict[nombre] = {0: 0, 1: 0, 2: 0}

        if puntaje is not None:
            data_dict[nombre][puntaje] = cantidad

    macroprocesos = []
    serie_0 = []
    serie_1 = []
    serie_2 = []

    for macro, valores in data_dict.items():
        macroprocesos.append(macro)
        serie_0.append(valores[0])
        serie_1.append(valores[1])
        serie_2.append(valores[2])

    return jsonify({
        "macroprocesos": macroprocesos,
        "serie_0": serie_0,
        "serie_1": serie_1,
        "serie_2": serie_2
    })
import os
import secrets
import app.constants as constants
from . import autoevaluacion_bp
from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from collections import defaultdict
from werkzeug.utils import secure_filename
from app.models import IpressEssalud
from app.models import CondicionCriterio, Fuente, Autoevaluacion, AutoevaluacionReporteCriterio
from app.models import Macroproceso, Estandar, Criterio, IpressEssalud, TipoObservacion
from app import db
from app.constants import MAPA_NIVEL
from sqlalchemy import and_, func, cast, String, case,select, literal, func, or_
from sqlalchemy.orm import aliased
from sqlalchemy.dialects.postgresql import insert


#----------------------------------------------------------------------------------------------
# Vista principal de la autoevaluacion para generar la AE para todas las Ipress
#----------------------------------------------------------------------------------------------
@autoevaluacion_bp.route("/iniciar", methods=["GET"])
@login_required
def iniciar():
    return render_template(
        "generarautoevaluacion.html",
        user=current_user,
        page_title="Generar Autoevaluacion para IPRESS"
    )


#----------------------------------------------------------------------------------------------
# Listado de la Ipress y sus Autoevaluaciones
#----------------------------------------------------------------------------------------------
@autoevaluacion_bp.route("/api/ipress-autoevaluacion")
def ipress_autoevaluacion():

    datos = (
        db.session.query(
            IpressEssalud.id_ipress,
            IpressEssalud.nombre_ipress,
            IpressEssalud.nivel_ipress,
            IpressEssalud.es_activo,
            Autoevaluacion.id_autoevaluacion,
            Autoevaluacion.estado
        )
        .outerjoin(
            Autoevaluacion,
            and_(
            Autoevaluacion.id_ipress == IpressEssalud.id_ipress,
            Autoevaluacion.periodo == constants.ACREDITACION_ACTUAL
        )
        )
        .all()
    )

    resultado = []

    for r in datos:
        resultado.append({
            "id_ipress": r.id_ipress,
            "nombre": r.nombre_ipress,
            "es_activo": r.es_activo,
            "nivel_ipress": r.nivel_ipress,
            "id_autoevaluacion": r.id_autoevaluacion,
            "estado": r.estado
        })

    return jsonify(resultado)

#----------------------------------------------------------------------------------------------
# Proceso para generar autoevaluacion del año y calificar criterios con fuentes precargadas
#----------------------------------------------------------------------------------------------
@autoevaluacion_bp.route("/api/autoevaluacionpuntajeautomatico/<int:IdIpress>", methods=["GET"])
@login_required
def calculo_puntaje_automatico(IdIpress):

    ipress = db.session.query(IpressEssalud).filter_by(id_ipress=IdIpress).first()
    columna_nombre = MAPA_NIVEL.get(ipress.nivel_ipress)
    id_anio_acreditacion = constants.ACREDITACION_ACTUAL
    id_evaluacion = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.id_ipress == IdIpress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .scalar()
    )
    print('datos -->',id_evaluacion)
    
    #Si no hay autoevaluacion crea uno nuevo, estado = 1  activo
    if id_evaluacion is None:
        autoevaluacion = Autoevaluacion(
            id_ipress=IdIpress,
            periodo=id_anio_acreditacion,
            estado=1)
        db.session.add(autoevaluacion)
        db.session.commit()
        id_evaluacion = autoevaluacion.id_autoevaluacion

    resultados = (
        db.session.query(
            Criterio.id_criterio,
            Criterio.codigo_criterio,
            func.count(CondicionCriterio.id_tecnica).label("total_requerido"),
            func.count(case(((Fuente.link_fuente != None) & (Fuente.link_fuente != ''), 1))).label("total_predefinido"))
        .outerjoin(CondicionCriterio,CondicionCriterio.id_criterio == Criterio.id_criterio)
        .outerjoin(Fuente,Fuente.id_condicion == CondicionCriterio.id_condicion)
        .filter(
            Criterio.aplica_essalud == 1,
            getattr(Criterio, columna_nombre) == 1
        )
        .group_by(Criterio.id_criterio,Criterio.codigo_criterio)
        .order_by(Criterio.id_criterio.asc())
        .all()
    )

    insertados = []
    for r in resultados:

        if r.total_requerido == r.total_predefinido:
            existe = (
                db.session.query(AutoevaluacionReporteCriterio)
                .filter(AutoevaluacionReporteCriterio.id_autoevaluacion == id_evaluacion)
                .filter(AutoevaluacionReporteCriterio.id_criterio == r.id_criterio)
                .first()
            )
                
            if not existe:
                nuevo = AutoevaluacionReporteCriterio(
                    id_autoevaluacion=id_evaluacion,
                    id_criterio=r.id_criterio,
                    puntaje_criterio=2,
                    es_precalificado=True
                )
                db.session.add(nuevo)
                insertados.append(r.id_criterio)

    db.session.commit()

    return {
        "mensaje": "Proceso completado",
        "criterios_insertados": insertados
    }
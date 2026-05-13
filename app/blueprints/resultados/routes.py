from . import resultados_bp
from .queries_autoevaluacion import get_autoevaluacion_detalle_list
from .word_export import generar_word_autoevaluacion
from flask import render_template, jsonify, request, send_file
from flask_login import login_required, current_user
from app import db
from sqlalchemy import func, literal
from sqlalchemy.orm import aliased
from collections import defaultdict
from app.constants import MAPA_NIVEL
from app.constants import ACREDITACION_ACTUAL
from app.models import (
    Fuente,
    CondicionCriterio,
    ProcesoInstitucional,
    Criterio,
    Estandar,
    Macroproceso,
    Autoevaluacion,
    AutoevaluacionReporte,
    AutoevaluacionReporteCriterio,
    IpressEssalud,
    RedEssalud,
    TecnicaEvaluacion
)


#----------------------------------------------------------------------
# Vista de Template de fuentes
#---------------------------------------------------------------------
@resultados_bp.route("/revisionfuentes")
@login_required
def revisionfuentes():
    id_rol = current_user.roles_asociados[0].rol.id_rol if current_user.roles_asociados else None  
    return render_template("fuentes.html",  current_user=current_user,
                           rol_id=id_rol, 
                           page_title="Revisión de Fuentes")


#----------------------------------------------------------------------
# Listado de fuentes para Gamcc
#---------------------------------------------------------------------
@resultados_bp.route("/api/autoevaluacion_detalle/<int:id_ipress>/id_mp/<int:id_mp>")
def autoevaluacion_detalle(id_ipress, id_mp):

    # Consulta cruzando ambas tablas
    query = (
        db.session.query(
            Autoevaluacion.id_autoevaluacion,
            IpressEssalud.nivel_ipress
        )
        .select_from(Autoevaluacion)
        .join(
            IpressEssalud,
            IpressEssalud.id_ipress == Autoevaluacion.id_ipress
        )
        .filter(
            Autoevaluacion.id_ipress == id_ipress,
            Autoevaluacion.periodo == ACREDITACION_ACTUAL
        )
    )
    # Imprimir SQL con valores reales
    print(
        query.statement.compile(
            db.engine,
            compile_kwargs={"literal_binds": True}
        )
    )
    # Ejecutar después de imprimir
    resultado = query.first()

    if not resultado:
        return jsonify([]), 200
    
    id_autoevaluacion = resultado[0]
    nivel_ipress = resultado[1]
    arc = aliased(AutoevaluacionReporteCriterio)
    ar = aliased(AutoevaluacionReporte)
    
    columna_nombre = MAPA_NIVEL.get(nivel_ipress)
    if not columna_nombre:
        return jsonify([]), 200
    columna_comparar = getattr(Criterio, columna_nombre)
    
    query = (
        db.session.query(
            RedEssalud.nombre_red,
            IpressEssalud.nombre_ipress,
            IpressEssalud.nivel_ipress,
            Macroproceso.codigo_macroproceso,
            (Macroproceso.codigo_macroproceso + ' - ' + Macroproceso.nombre_macroproceso).label("nombre_mp"),
            Criterio.codigo_criterio,
            (Criterio.codigo_criterio + ' - ' + Criterio.nombre_criterio).label("nombre_criterio"),
            Criterio.puntaje_0_txt,
            Criterio.puntaje_1_txt,
            Criterio.puntaje_2_txt,
            Criterio.nivel_i_1,
            Criterio.nivel_i_2,
            Criterio.nivel_i_3,
            Criterio.nivel_i_4,
            Criterio.nivel_ii_1,
            Criterio.nivel_ii_2,
            Criterio.nivel_iii_1,
            arc.puntaje_criterio,
            CondicionCriterio.nombre_condicion,
            TecnicaEvaluacion.id_tecnica,
            TecnicaEvaluacion.nombre_tecnica,
            ProcesoInstitucional.nombre_proceso,
            Fuente.nombre_fuente,
            Fuente.link_fuente,
            ar.ruta_archivo,
            ar.link_reporte
        )
        .select_from(Autoevaluacion) 
        .join(IpressEssalud, IpressEssalud.id_ipress == Autoevaluacion.id_ipress)
        .join(RedEssalud, RedEssalud.id_red == IpressEssalud.id_red)
        .outerjoin(Macroproceso, db.true())
        .outerjoin(Estandar, Estandar.id_macroproceso == Macroproceso.id_macroproceso)
        .outerjoin(Criterio, Criterio.id_estandar == Estandar.id_estandar)
        .outerjoin(ProcesoInstitucional, ProcesoInstitucional.id_proceso == Criterio.id_proceso)
        .outerjoin(CondicionCriterio, CondicionCriterio.id_criterio == Criterio.id_criterio)
        .outerjoin(TecnicaEvaluacion, TecnicaEvaluacion.id_tecnica == CondicionCriterio.id_tecnica)
        .outerjoin(Fuente, Fuente.id_condicion == CondicionCriterio.id_condicion)
        .outerjoin(
            arc,
            (arc.id_criterio == Criterio.id_criterio) &
            (arc.id_autoevaluacion == Autoevaluacion.id_autoevaluacion)
        )
        .outerjoin(
            ar,
            (ar.id_fuente == Fuente.id_fuente) &
            (ar.id_autoevaluacion == Autoevaluacion.id_autoevaluacion)
        )
        .filter(
            Autoevaluacion.id_autoevaluacion == id_autoevaluacion,
            Criterio.aplica_essalud.is_(True)
        )
    )
    #WHERE DINÁMICO POR NIVEL
    if columna_comparar is not None:
        query = query.filter(columna_comparar.is_(True))
        
    if id_mp is not None and id_mp != 0:
        query = query.filter(Macroproceso.id_macroproceso ==id_mp)
        
    query = query.order_by(
        Macroproceso.id_macroproceso,
        Estandar.id_estandar,
        Criterio.id_criterio,
        CondicionCriterio.id_condicion
    )
    
    print(
        query.statement.compile(
            db.engine,
            compile_kwargs={"literal_binds": True}
        )
    )

    result = query.all()
    data = [dict(row._mapping) for row in result]
    return jsonify(data)


@resultados_bp.route("/export/word_autoevaluacion/<int:id_ipress>/id_mp/<int:id_mp>")
@login_required
def export_word_autoevaluacion(id_ipress, id_mp):
    rows = get_autoevaluacion_detalle_list(id_ipress, id_mp)
    if not rows:
        return jsonify({"error": "No hay datos para exportar"}), 404
    nombre = rows[0].get("nombre_ipress") or f"ipress_{id_ipress}"
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in str(nombre))[:100]
    bio = generar_word_autoevaluacion(rows, nombre_ipress=nombre)
    fname = f"Hoja_Autoevaluacion_{safe.strip() or id_ipress}.docx"
    return send_file(
        bio,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=fname,
    )
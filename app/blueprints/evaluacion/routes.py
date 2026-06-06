import os
import secrets
import json
import app.constants as constants
from . import evaluacion_bp
from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from collections import defaultdict
from werkzeug.utils import secure_filename
from app.models import IpressEssalud, RedEssalud
from app.models import TecnicaEvaluacion, CondicionCriterio, Fuente, ProcesoInstitucional, Autoevaluacion, AutoevaluacionReporte, AutoevaluacionReporteCriterio, AutoevaluacionReporteComentario, AutoevaluacionComentarioTecnica
from app.models import Macroproceso, Estandar, Criterio, IpressEssalud, TipoObservacion, AutoevaluacionTecnicaObservacion
from app import db
from app.constants import MAPA_NIVEL
from sqlalchemy.dialects import oracle
from sqlalchemy import and_, func, cast, String, select, literal, func, or_, case
from sqlalchemy.orm import aliased


def ruta_archivo_a_url_publica(ruta_archivo):
    """
    Convierte la ruta guardada en BD (relativa o absoluta, con \\ en Windows)
    en URL válida para el navegador bajo /uploads/...
    """
    if not ruta_archivo:
        return ""
    s = os.path.normpath(str(ruta_archivo)).replace("\\", "/")
    low = s.lower()
    idx = low.find("uploads/")
    if idx >= 0:
        return "/" + s[idx:].replace("//", "/")
    return "/uploads/fuentes/" + os.path.basename(s)


#-----------------------------------------------------------------------
# Evaluador: Vista de Lista de Macroprocesos 
#-----------------------------------------------------------------------
@evaluacion_bp.route("/listado", methods=["GET"])
@login_required
def evaluar_ae():

    id_anio_acreditacion = constants.ACREDITACION_ACTUAL
    IdIpress = getattr(current_user, "id_ipress", None)
    
    IdAutoevaluacion = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.id_ipress == IdIpress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .scalar()
    )
    
    resultado = (
        db.session.query(
            Autoevaluacion.id_autoevaluacion,
            Autoevaluacion.estado,
            Autoevaluacion.id_ipress,
        )
        .filter(Autoevaluacion.id_ipress == IdIpress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .first()
    )

    estado_ae = None
    id_ipress_export = IdIpress
    if resultado:
        IdAutoevaluacion = resultado.id_autoevaluacion
        estado_ae = resultado.estado
        id_ipress_export = resultado.id_ipress or IdIpress

    return render_template(
        "listamacroproceso.html",
        user=current_user,
        IdAutoevaluacion=IdAutoevaluacion,
        estado_ae=estado_ae,
        id_ipress_export=id_ipress_export,
        page_title="Autoevaluación por Macroproceso",
    )

#-----------------------------------------------------------------------
# Evaluador: Datatable MP y avance 
#-----------------------------------------------------------------------
@evaluacion_bp.route("/api/calculoavance/<int:IdIpress>", methods=["GET"])
@login_required
def calculo_avance(IdIpress):

    id_anio_acreditacion = constants.ACREDITACION_ACTUAL
    id_evaluacion = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.id_ipress == IdIpress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .scalar()
    )
    print(id_evaluacion)
       
    ipress = db.session.query(IpressEssalud).filter_by(id_ipress=IdIpress).first()
    columna_nombre = MAPA_NIVEL.get(ipress.nivel_ipress)
    
    query = (
        db.session.query(
            Macroproceso.id_macroproceso,
            Macroproceso.codigo_macroproceso,
            Macroproceso.nombre_macroproceso,
            func.count(AutoevaluacionReporteCriterio.id_criterio).label("total_calificados"),
            func.count(Criterio.id_criterio).label("total_criterios")
        )
        .outerjoin(Estandar, Estandar.id_macroproceso == Macroproceso.id_macroproceso)
        .outerjoin(Criterio, Criterio.id_estandar == Estandar.id_estandar)
        .outerjoin(
            AutoevaluacionReporteCriterio,
            and_(
                AutoevaluacionReporteCriterio.id_criterio == Criterio.id_criterio,
                AutoevaluacionReporteCriterio.id_autoevaluacion == id_evaluacion
            )
        )
        .filter(
            getattr(Criterio, columna_nombre) == 1,
            Criterio.aplica_essalud == 1
        )
        .group_by(
            Macroproceso.id_macroproceso,
            Macroproceso.codigo_macroproceso,
            Macroproceso.nombre_macroproceso
        )
        .order_by(Macroproceso.id_macroproceso)
    )

    result = query.all()
    data = []

    for r in result:
        porcentaje = round((r.total_calificados / r.total_criterios * 100) if r.total_criterios else 0, 2)
        
        data.append({
            "id_macroproceso": r.id_macroproceso,
            "codigo_macroproceso": r.codigo_macroproceso,
            "total_criterios": r.total_criterios,
            "total_criterios_reportados": r.total_calificados,
            "nombre_macroproceso": r.nombre_macroproceso,
            "avance": f"{porcentaje} % ",
            "id_autoevaluacion": id_evaluacion
        })


    return jsonify(data)

#-----------------------------------------------------------------------
# Evaluador: Vista Listado Estandares y Criterios
#-----------------------------------------------------------------------
@evaluacion_bp.route("/reportaevaluador", methods=["POST"])
@login_required
def reportaevaluador():
    id_autoevaluacion= request.form.get("id_autoevaluacion")
    id_macroproceso= request.form.get("id_macroproceso")
    id_criterio= request.form.get("id_criterio")
    id_estandar= request.form.get("id_estandar")
    nombre_macroproceso = request.form.get("nombre_macroproceso")   
    return render_template(
        "reportaevaluador.html",
        user=current_user,
        page_title="Reporte de Autoevaluación",
        id_autoevaluacion=id_autoevaluacion,
        id_macroproceso=id_macroproceso,
        id_criterio=id_criterio,
        id_estandar=id_estandar,
        nombre_macroproceso=nombre_macroproceso
    )
    
#-----------------------------------------------------------------------
# Datatable: Lista de Estandares y Criterios
#-----------------------------------------------------------------------
@evaluacion_bp.route("api/reportatabla", methods=["GET","POST"])
@login_required
def reportatabla():
    id_macroproceso = request.args.get("id_macroproceso")    
    id_estandar = request.args.get("id_estandar")
    id_ipress = getattr(current_user, "id_ipress", None)
    
    id_anio_acreditacion = constants.ACREDITACION_ACTUAL
    id_ae = (
        db.session.query(
            Autoevaluacion.id_autoevaluacion
        )
        .filter(Autoevaluacion.id_ipress == id_ipress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .first()
    )
    ipress = db.session.query(IpressEssalud).filter_by(id_ipress=id_ipress).first()
    columna_nombre = MAPA_NIVEL.get(ipress.nivel_ipress)
    if not columna_nombre:
        return jsonify([]), 200
    columna_comparar = getattr(Criterio, columna_nombre)    
    query = (
        db.session.query(
            Estandar.codigo_estandar,
            Estandar.nombre_estandar,
            Criterio.id_criterio,
            Criterio.codigo_criterio,
            Criterio.nombre_criterio,
            Criterio.total_condiciones,
            CondicionCriterio.puntaje_condicion,
            AutoevaluacionReporteCriterio.puntaje_criterio.label("calificacion_criterio"),
            AutoevaluacionReporteCriterio.es_precalificado,
            func.count(Fuente.id_fuente).label("cantidad_a_reportar")
        )
        .outerjoin(
            Criterio,
            Criterio.id_estandar == Estandar.id_estandar,
        )
        .outerjoin(
            AutoevaluacionReporteCriterio,
            and_(
                AutoevaluacionReporteCriterio.id_criterio == Criterio.id_criterio,
                AutoevaluacionReporteCriterio.id_autoevaluacion == id_ae[0]
            )
        )
        .outerjoin(
            CondicionCriterio,
            CondicionCriterio.id_criterio == Criterio.id_criterio
        )
        .outerjoin(
            Fuente,
            Fuente.id_condicion == CondicionCriterio.id_condicion
        )
        .filter(
            Estandar.id_macroproceso == id_macroproceso
        )
        .filter(Criterio.aplica_essalud == 1)        
        .group_by(
            Estandar.id_estandar,
            Estandar.codigo_estandar,
            Estandar.nombre_estandar,
            Criterio.id_criterio,
            Criterio.codigo_criterio,
            Criterio.nombre_criterio,
            Criterio.total_condiciones,
            CondicionCriterio.puntaje_condicion,
            AutoevaluacionReporteCriterio.puntaje_criterio,
            AutoevaluacionReporteCriterio.es_precalificado
        )
        .order_by(Criterio.codigo_criterio)
    )

    if id_macroproceso not in ["", None, "0", "null", "NULL"]:
            query = query.filter(Estandar.id_macroproceso == int(id_macroproceso))

    if id_estandar not in ["", None, "0", "null", "NULL"]:
        query = query.filter(Estandar.id_estandar == int(id_estandar))
        
    #WHERE DINÁMICO POR NIVEL
    if columna_comparar is not None:
        query = query.filter(columna_comparar == 1)

    print(
        query.statement.compile(
            dialect=oracle.dialect(),
            compile_kwargs={"literal_binds": True}
        )
    )
    rows = db.session.execute(query).all()
    
    return jsonify([
        {
            "estandar": f"{r.codigo_estandar}  {r.nombre_estandar}",
            "criterio": f"{r.codigo_criterio}  {r.nombre_criterio}",
            "id_criterio": f"{r.id_criterio}",
            "cantidad_a_reportar": f"{r.cantidad_a_reportar}",
            "puntaje_criterio": f"{r.puntaje_condicion}",
            "puntaje_es_precalificado": f"{r.es_precalificado}",
            "cantidad_condiciones": f"{r.total_condiciones}",
            "calificacion_criterio": f"{r.calificacion_criterio}",
            "regla_puntaje2_condicion": (
                r.puntaje_condicion == 2 and r.total_condiciones == 1
        )
        }
        for r in rows
    ])

#-----------------------------------------------------------------------
#Vista: Evaluador ve lista de Fuentes reportadas
#-----------------------------------------------------------------------
@evaluacion_bp.route("/validar", methods=["POST"])
@login_required
def evaluador_reporte():
    id_autoevaluacion = request.form.get("id_autoevaluacion")
    id_criterio = request.form.get("id_criterio")
    nombre_criterio = request.form.get("nombre_criterio")
    cantidad_a_reportar = request.form.get("cantidad_a_reportar")
    es_precalificado = request.form.get("es_precalificado")
    puntaje_actual_criterio = request.form.get("puntaje_actual_criterio")
    regla_puntaje2_1condicion = request.form.get("regla_puntaje2_1condicion")
    
    resultado = (
        db.session.query(
            Macroproceso.id_macroproceso,
            (Macroproceso.codigo_macroproceso + " - " +  Macroproceso.nombre_macroproceso).label("nombre_macroproceso")
        )
        .join(Estandar, Estandar.id_macroproceso == Macroproceso.id_macroproceso)
        .join(Criterio, Criterio.id_estandar == Estandar.id_estandar)
        .filter(Criterio.id_criterio == id_criterio)
        .first()
    )
    
    if resultado:
        id_macro = resultado.id_macroproceso
        nombre_macro = resultado.nombre_macroproceso
    
    return render_template(
        "validarreportado.html",
        user=current_user,
        id_macroproceso=id_macro,
        nombre_macroproceso=nombre_macro,
        id_autoevaluacion=id_autoevaluacion,
        id_criterio= id_criterio,
        nombre_criterio= nombre_criterio,
        cantidad_a_reportar= cantidad_a_reportar,
        es_precalificado= es_precalificado,
        regla_puntaje2_1condicion = regla_puntaje2_1condicion,
        puntaje_actual_criterio = puntaje_actual_criterio,
        page_title=f"Validar Reporte del Evaluado"
    )
    

#-----------------------------------------------------------------------------------
#API: Para obtener de acuerdo al criterio y la autoevaluacion el valor del puntaje
#------------------------------------------------------------------------------------
@evaluacion_bp.route("api/getpuntajecriterio/<int:id_criterio>/id_ae/<int:id_ae>", methods=["GET"])
@login_required
def get_puntaje_criterio(id_criterio,id_ae):
        
    puntaje_criterio = AutoevaluacionReporteCriterio.query.filter_by(
        id_autoevaluacion=id_ae,
        id_criterio=id_criterio
    ).first()
    puntaje_valor = puntaje_criterio.puntaje_criterio if puntaje_criterio else None

    return jsonify({
        "puntaje_criterio": puntaje_valor
    })

#----------------------------------------------------------------------------------------------------------
#Datatable: Evaluador Obtiene lista de Fuentes reportadas
#----------------------------------------------------------------------------------------------------------
@evaluacion_bp.route("api/getevaluadorreporte/<int:id_criterio>/id_ae/<int:id_ae>", methods=["GET"])
@login_required
def get_evaluador_reporte(id_criterio,id_ae):
    
    #Obtener los archivos de la ae
    archivos_all = AutoevaluacionTecnicaObservacion.query.filter_by(id_autoevaluacion=id_ae).all()
    archivos_map = defaultdict(list)
    archivos_vistos_por_condicion = defaultdict(set)

    for a in archivos_all:
        upload_fn = os.path.basename(a.ruta_archivo)
        if upload_fn in archivos_vistos_por_condicion[a.id_condicion]:
            continue
        archivos_vistos_por_condicion[a.id_condicion].add(upload_fn)
        archivos_map[a.id_condicion].append({
            "nombre": a.nombre_archivo,
            "ruta": a.ruta_archivo,
            "ruta_url": ruta_archivo_a_url_publica(a.ruta_archivo),
            "upload_filename": upload_fn
        })
        
    
    tipos = TipoObservacion.query.all()
    puntaje_criterio = AutoevaluacionReporteCriterio.query.filter_by(
        id_autoevaluacion=id_ae,
        id_criterio=id_criterio
    ).first()
    puntaje_valor = puntaje_criterio.puntaje_criterio if puntaje_criterio else None

    resultados_de_precalificados = (
            db.session.query(
                Criterio.id_criterio,
                Criterio.codigo_criterio,
                func.count(CondicionCriterio.id_tecnica).label("total_requerido"),
                func.count(
                    case(
                        (CondicionCriterio.id_tecnica == 4, 1)
                    )
                ).label("total_tecnica_requerido_documentos"),
                func.count(
                    case(
                        (AutoevaluacionReporte.id_aereporte.is_(None),1)
                    )
                ).label("total_sin_reporte"),                
                func.count(
                    case(
                        (
                            and_(
                                Fuente.link_fuente.isnot(None),
                                func.length(Fuente.link_fuente) > 0
                            ),
                            1
                        ),
                        else_=None
                    )
                ).label("total_archivos_predefinidos") 
            )
            .outerjoin(CondicionCriterio, CondicionCriterio.id_criterio == Criterio.id_criterio)
            .outerjoin(Fuente,Fuente.id_condicion == CondicionCriterio.id_condicion)
            .outerjoin(AutoevaluacionReporte, and_(AutoevaluacionReporte.id_fuente == Fuente.id_fuente,AutoevaluacionReporte.id_autoevaluacion == id_ae))
            .filter(Criterio.id_criterio == id_criterio)
            .group_by(Criterio.id_criterio, Criterio.codigo_criterio)
            .all()
    )

    for r in resultados_de_precalificados:    
        boton_grabar = 1
        #Si todas las fuentes son documentos y no he subido nada de archivos entonces puntaje = 0    
        if (r.total_requerido == r.total_tecnica_requerido_documentos) and  (r.total_tecnica_requerido_documentos == r.total_sin_reporte) and (r.total_archivos_predefinidos == 0):
            boton_grabar = 0
                    
        #Si todas las fuentes que requiero son documentos y el total de documentos esta predefinido entonces puntaje = 2    
        if (r.total_requerido ==r.total_tecnica_requerido_documentos) and (r.total_tecnica_requerido_documentos==r.total_archivos_predefinidos):
            boton_grabar = 0
                    
        if (r.total_requerido ==r.total_tecnica_requerido_documentos) and  (r.total_tecnica_requerido_documentos == r.total_sin_reporte)  and (r.total_archivos_predefinidos > 0):   
            boton_grabar = 0
        
    AR = aliased(AutoevaluacionReporte)
    AER = aliased(AutoevaluacionReporteComentario)
    ACT = aliased(AutoevaluacionComentarioTecnica)
    query = (
        db.session.query(
            Criterio.id_criterio,
            Criterio.nombre_criterio,
            Criterio.puntaje_0_txt,
            Criterio.puntaje_1_txt,
            Criterio.puntaje_2_txt,
            CondicionCriterio.id_condicion,
            CondicionCriterio.nombre_condicion,
            CondicionCriterio.puntaje_condicion,
            CondicionCriterio.tipo_condicion,
            TecnicaEvaluacion.id_tecnica,
            TecnicaEvaluacion.nombre_tecnica,
            Fuente.id_fuente,
            Fuente.nombre_fuente,
            Fuente.link_fuente,
            AR.id_aereporte,
            AR.id_tiporeporte,
            AR.id_fuente.label("rep_id_fuente"),
            AR.link_reporte,
            AR.nombre_archivo,
            AR.ruta_archivo,
            AR.puntaje_reporte,
            AER.es_observado,
            TipoObservacion.id_tipo_observacion,
            ACT.es_observado.label('es_observada_tecnica')
        )
        .outerjoin(
            CondicionCriterio,
            CondicionCriterio.id_criterio == Criterio.id_criterio
        )
        .outerjoin(
            TecnicaEvaluacion,
            TecnicaEvaluacion.id_tecnica == CondicionCriterio.id_tecnica
        )
        .outerjoin(
            Fuente,
            Fuente.id_condicion == CondicionCriterio.id_condicion
        )
        .outerjoin(
            AR,
            and_(
                AR.id_fuente == Fuente.id_fuente,
                AR.id_autoevaluacion == id_ae
            )
        )
        .outerjoin(
            AER,
            and_(
                AER.id_fuente == Fuente.id_fuente,
                AER.id_autoevaluacion == id_ae
            )
        )
        .outerjoin(
            ACT,
            and_(
                ACT.id_condicion == CondicionCriterio.id_condicion,
                ACT.id_autoevaluacion == id_ae
            )
        )
        .outerjoin(
            TipoObservacion,
                TipoObservacion.id_tipo_observacion == AER.observacion_fuente
        )
        .filter(
            Criterio.aplica_essalud == 1,
            Criterio.id_criterio == id_criterio
        )
        .order_by(CondicionCriterio.id_condicion)
    )

    '''print(
        query.statement.compile(
            db.engine,
            compile_kwargs={"literal_binds": True}
        )
    )'''
    resultados = query.all()

    data = []

    for r in resultados:
        str_draw_puntaje = ''
        str_draw_check = ''
        html_select_observaciones=''
        str_input_valor = ''
        #Es para la tecnica revision documental
        if r.id_tecnica == 4:     
            
            #cuando la fuente es predefinida check por defecto
            if r.link_fuente:
                icon_check = ('<i class="fa fa-check-circle text-success" style="font-size:3rem;"></i>')
                icon_x = ('<i class="fa fa-times-circle text-muted" style="font-size:3rem;"></i>')
                html_select_observaciones=''
                str_input_valor = f'<input type="hidden" name="valor_{r.id_condicion}_{r.id_fuente}" class="valor_set" data-tecnica="{r.id_tecnica}" value="1">'
                str_draw_check = f'{icon_check}&nbsp;&nbsp;{icon_x}'  
                        
            #cuando no hay nada reportado X por defecto    
            if not r.link_reporte and not r.nombre_archivo and not r.link_fuente:
                icon_check = ('<i class="fa fa-check-circle text-muted" style="font-size:3rem;"></i>')
                icon_x = ('<i class="fa fa-times-circle text-danger" style="font-size:3rem;"></i>')
                html_select_observaciones=''
                str_input_valor = f'<input type="hidden" name="valor_{r.id_condicion}_{r.id_fuente}" class="valor_set" data-tecnica="{r.id_tecnica}" value="0">'
                str_draw_check = f'{icon_check}&nbsp;&nbsp;{icon_x}'  
                
            #si hay algo reportado
            if any([r.link_reporte, r.nombre_archivo]):
                if r.es_observado == 1:
                    icon_check = f'<a href="javascript:void(0)" class="btn_approve"><i class="fa fa-check-circle text-success" data-idcondicion="{r.id_condicion}" data-idfuente="{r.id_fuente}" style="font-size:3rem;"></i></a>'
                    icon_x = f'<a href="javascript:void(0)" class="btn_disapprove"><i class="fa fa-times-circle text-muted" data-idcondicion="{r.id_condicion}" data-idfuente="{r.id_fuente}" style="font-size:3rem;"></i></a><div id="set_select_observaciones_{r.id_fuente}"></div>'
                    html_select_observaciones=''
                    str_input_valor = f'<input type="hidden" name="valor_{r.id_condicion}_{r.id_fuente}" class="valor_set" data-tecnica="{r.id_tecnica}" value="1" >'
                    str_draw_check = f'{icon_check}&nbsp;&nbsp;{icon_x}'  
            
                if r.es_observado == 0:
                    icon_check = f'<a href="javascript:void(0)" class="btn_approve"><i class="fa fa-check-circle text-muted" data-idcondicion="{r.id_condicion}" data-idfuente="{r.id_fuente}" style="font-size:3rem;"></i></a>'
                    icon_x = f'<a href="javascript:void(0)" class="btn_disapprove"><i class="fa fa-times-circle text-danger" data-idcondicion="{r.id_condicion}" data-idfuente="{r.id_fuente}"  style="font-size:3rem;"></i></a>'
                    str_input_valor =f'<input type="hidden" name="valor_{r.id_condicion}_{r.id_fuente}" class="valor_set" data-tecnica="{r.id_tecnica}" value="1">'
                    html_select_observaciones=f'<div id="set_select_observaciones_{r.id_fuente}">'
                    html_select_observaciones += f'<select name="tipoObservacion_{r.id_fuente}"  id="tipoObservacion_{r.id_fuente}"  class="select_observacion form-select form-select-sm w-auto">'
                    html_select_observaciones += '<option value=""></option>'
                    for t in tipos:
                        selected = "selected" if t.id_tipo_observacion == r.id_tipo_observacion else ""
                        html_select_observaciones += f'''
                            <option value="{t.id_tipo_observacion}" {selected}>
                                {t.nombre_tipo_observacion}
                            </option>'''
                    html_select_observaciones += '</select></div>'
                    str_draw_check = f'{icon_check}&nbsp;&nbsp;{icon_x}'  
                    
                if r.es_observado == "" or r.es_observado is None:
                    icon_check = f'<a href="javascript:void(0)" class="btn_approve"><i class="fa fa-check-circle text-muted" data-idcondicion="{r.id_condicion}" data-idfuente="{r.id_fuente}" style="font-size:3rem;"></i></a>'
                    icon_x = f'<a href="javascript:void(0)" class="btn_disapprove"><i class="fa fa-times-circle text-muted" data-idcondicion="{r.id_condicion}" data-idfuente="{r.id_fuente}" style="font-size:3rem;"></i></a><div id="set_select_observaciones_{r.id_fuente}"></div>'
                    html_select_observaciones=''
                    str_input_valor = f'<input type="hidden" name="valor_{r.id_condicion}_{r.id_fuente}" class="valor_set" data-tecnica="{r.id_tecnica}" value="">'
                    str_draw_check = f'{icon_check}&nbsp;&nbsp;{icon_x}'     
            
            if r.puntaje_condicion == 2:
                str_draw_puntaje = '<select name="valor_'+str(r.id_fuente)+'" class="select_fuente_value form-select form-select-sm w-auto" >'
                str_draw_puntaje +='<option value="0">'+r.puntaje_0_txt+'</option>'
                str_draw_puntaje +='<option value="1">'+r.puntaje_1_txt+'</option>'              
                str_draw_puntaje +='<option value="2">'+r.puntaje_2_txt+'</option>'               
                str_draw_puntaje +='</select>'
    
        #Para las otras tecnicas    
        else:
            html_select_observaciones= ''
            str_draw_check = ''
            str_draw_puntaje=''
            str_input_valor=''
            if r.puntaje_condicion == 1:
                icon_check = ('<a href="javascript:void(0)" class="btn_approve">'
                    f'<i class="fa fa-check-circle '
                    f'{"text-success" if r.es_observada_tecnica == 1 else "text-muted"}" '
                    'style="font-size:3rem;" data-tecnica="'f'{r.id_tecnica}" data-condicion="'f'{r.id_condicion}" ></i></a>'
                )
                icon_x = (
                    '<a href="javascript:void(0)" class="btn_disapprove">'
                    f'<i class="fa fa-times-circle '
                    f'{"text-danger" if r.es_observada_tecnica == 0 else "text-muted"}" '
                    'style="font-size:3rem;" data-tecnica="'f'{r.id_tecnica}" data-condicion="'f'{r.id_condicion}" ></i></a>'
                )                                
                str_input_valor = '<input type="hidden" name="valor_'+str(r.id_condicion)+'" class="valor_set" value="0">'
                str_draw_check = f'{icon_check}&nbsp;&nbsp;{icon_x}'
    
            if r.puntaje_condicion == 2:               
                str_draw_puntaje = '<select name="valor_'+str(r.id_fuente)+'" class="select_fuente_value form-select form-select-sm w-auto" >'
                str_draw_puntaje +='<option value="0">'+r.puntaje_0_txt+'</option>'
                str_draw_puntaje +='<option value="1">'+r.puntaje_1_txt+'</option>'              
                str_draw_puntaje +='<option value="2">'+r.puntaje_2_txt+'</option>'               
                str_draw_puntaje +='</select>'
        
        archivos = []
        if r.id_tecnica == 3:
            archivos = archivos_map[r.id_condicion]
        
        data.append({
            "id_criterio": r.id_criterio,
            "nombre_criterio": r.nombre_criterio,
            "puntaje_0_txt": r.puntaje_0_txt,
            "puntaje_1_txt": r.puntaje_1_txt,
            "puntaje_2_txt": r.puntaje_2_txt,
            "id_condicion": r.id_condicion,
            "nombre_condicion": r.nombre_condicion,
            "puntaje_condicion": r.puntaje_condicion,
            "tipo_condicion": r.tipo_condicion,
            "id_tecnica": r.id_tecnica,
            "nombre_tecnica": r.nombre_tecnica,
            "id_fuente": r.id_fuente,
            "nombre_fuente": r.nombre_fuente,
            "link_fuente": r.link_fuente,
            "rep_id_autoevaluacion_reporte": r.id_aereporte,
            "tipo_reporte": r.id_tiporeporte,
            "rep_id_fuente": r.rep_id_fuente,
            "rep_link_reporte": r.link_reporte,
            "rep_nombre_archivo": r.nombre_archivo,
            "rep_ruta_archivo": r.ruta_archivo,
            "rep_puntaje_reporte": r.puntaje_reporte,
            "es_observado": r.es_observado,
            "checks": str_draw_check,
            "select_puntajes": str_draw_puntaje,
            "select_observaciones": html_select_observaciones,
            "valor_fuente": str_input_valor,
            "id_tipo_observacion": r.id_tipo_observacion,
            "archivos": archivos
        })
        
    return jsonify({
        "data": data,
        "select_puntajes2": str_draw_puntaje,
        "puntaje_criterio": puntaje_valor,
        "boton_grabar" : boton_grabar
    })


def sync_archivos_autoevaluacion(id_autoevaluacion, files_data):
    """
    Sincroniza archivos entre frontend (Dropzone) y BD.

    :param id_autoevaluacion: int
    :param files_data: list -> [
        {
            "id_condicion": 266,
            "files": [
                {"real_filename": "a.jpg", "upload_filename": "123.jpg"}
            ]
        }
    ]
    """

    #Traer lo de BD
    existentes = AutoevaluacionTecnicaObservacion.query.filter_by(
        id_autoevaluacion=id_autoevaluacion
    ).all()

    #Mapear BD
    db_map = {}
    for a in existentes:
        filename = os.path.basename(a.ruta_archivo)
        key = (a.id_condicion, filename)
        db_map[key] = a

    #Mapear Frontend
    frontend_map = {}
    for item in files_data or []:
        id_condicion = int(item.get("id_condicion"))

        for f in item.get("files", []):
            key = (id_condicion, f.get("upload_filename"))
            frontend_map[key] = f

    #Eliminar los que ya existen
    for key, registro in db_map.items():

        if key not in frontend_map:
            # eliminar archivo físico
            if registro.ruta_archivo and os.path.exists(registro.ruta_archivo):
                try:
                    os.remove(registro.ruta_archivo)
                except Exception as e:
                    print(f"Error eliminando archivo: {e}")
            # eliminar de BD
            db.session.delete(registro)

    #Insertar Nuevos
    for key, f in frontend_map.items():
        if key not in db_map:
            id_condicion, filename = key
            temp_path = os.path.join("uploads/temp_fuentes", filename)
            final_path = os.path.join("uploads/fuentes", filename)
            # mover archivo si existe en temp
            if os.path.exists(temp_path):
                try:
                    os.rename(temp_path, final_path)
                except Exception as e:
                    print(f"Error moviendo archivo: {e}")

            nuevo = AutoevaluacionTecnicaObservacion(
                id_autoevaluacion=id_autoevaluacion,
                id_condicion=id_condicion,
                nombre_archivo=f.get("real_filename"),
                ruta_archivo=final_path
            )

            db.session.add(nuevo)

    #GUARDAR CAMBIOS
    db.session.commit()


#-----------------------------------------------------------------------
#Form: Grabar el puntaje calculado
#-----------------------------------------------------------------------
@evaluacion_bp.route("/grabarcalculocriterio", methods=["POST"])
@login_required
def upsert_autoevaluacion():
    data = request.get_json()
    id_autoevaluacion = data.get("id_autoevaluacion")
    id_criterio = data.get("id_criterio_calcular")
    puntaje = data.get("puntaje_total_criterio")
    fuentes_data = data.get("fuentes_data",[])
    condiciones_data = data.get("condiciones_data",[])
    files_json = data.get("filesToSend")
    files_data = json.loads(files_json) if files_json else []
      
    try: 

        sync_archivos_autoevaluacion(id_autoevaluacion, files_data)

        for item in files_data:
            id_condicion = item.get("id_condicion")
            files = item.get("files", [])
            for f in files:
                nombre_real = f.get("real_filename")
                nombre_servidor = f.get("upload_filename")
                temp_path = os.path.join("uploads/temp_fuentes", nombre_servidor)
                final_dir = os.path.join("uploads/fuentes")
                final_path = os.path.join(final_dir, nombre_servidor)
                #crear solo carpeta principal (una vez)
                os.makedirs(final_dir, exist_ok=True)
                if os.path.exists(temp_path):
                    os.rename(temp_path, final_path)
                nuevo = AutoevaluacionTecnicaObservacion(
                    id_autoevaluacion=id_autoevaluacion,
                    id_condicion=id_condicion,
                    nombre_archivo=nombre_real,
                    ruta_archivo=final_path
                )
                db.session.add(nuevo)
    
        #Insertar/actualizar criterios
        registro = AutoevaluacionReporteCriterio.query.filter_by(
            id_autoevaluacion=id_autoevaluacion,
            id_criterio=id_criterio
        ).first()

        if registro:

            registro.puntaje_criterio = puntaje

        else:

            nuevo = AutoevaluacionReporteCriterio(
                id_autoevaluacion=id_autoevaluacion,
                id_criterio=id_criterio,
                puntaje_criterio=puntaje,
                es_precalificado=False
            )

            db.session.add(nuevo)

        db.session.commit()

        #Insertar/actualizar fuentes manualmente, si la fuente tiene observaciones se guarda el id_observacion
        for f in fuentes_data:
            idf = int(f["id_fuente"])
            valor_fuente = f.get("valor_fuente")

            # Si viene vacío no hacer nada
            if valor_fuente == "" or valor_fuente is None:
                continue

            valor = int(valor_fuente)

            valorSelectObs = f.get("valorSelectObs")
            valorSelectObs = int(valorSelectObs) if valorSelectObs else None

            updated = db.session.query(AutoevaluacionReporteComentario).filter_by(
                id_autoevaluacion=id_autoevaluacion,
                id_fuente=idf
            ).update({
                "es_observado": valor,
                "observacion_fuente": valorSelectObs
            })

            if updated == 0:
                nuevo = AutoevaluacionReporteComentario(
                    id_autoevaluacion=id_autoevaluacion,
                    id_fuente=idf,
                    es_observado=valor,
                    observacion_fuente=valorSelectObs
                )
                db.session.add(nuevo)
        
        #Insertar/actualizar condiciones para otras tecnicas diferentes a revision documental
        for c in condiciones_data:
            idc = int(c["id_condicion"])
            valor = int(c["valor_condicion"])            
            updated_condicion = db.session.query(AutoevaluacionComentarioTecnica).filter_by(
                id_autoevaluacion=id_autoevaluacion,
                id_condicion=idc
            ).update({"es_observado": valor})
            
            if updated_condicion == 0:
                nueva_condicion = AutoevaluacionComentarioTecnica(
                    id_autoevaluacion=id_autoevaluacion,
                    id_condicion=idc,
                    es_observado=valor
                )
                db.session.add(nueva_condicion)

        #Insertar/Eliminar files de las evidencias


        #Commit final
        db.session.commit()
        mensaje = 'Puntaje y Observaciones actualizadas correctamente' 
        return jsonify({'success': True, 'mensaje': mensaje})
    
    except Exception as e:
        db.session.rollback()
        mensaje = 'Puntaje no pudo actualizarse'
        return jsonify({'success': False, 'mensaje': mensaje, 'error': str(e)}), 500
    
    
#-----------------------------------------------------------------------
# Guardar el Estado de la Autoevaluacion 1:activo 2:desactivado
# Buscar los criterios que no tienen fuentes y califica a 0
#-----------------------------------------------------------------------
@evaluacion_bp.route('/actualizar-estado', methods=['POST'])
def actualizar_estado():

    try:
        data = request.get_json()
        id_autoevaluacion = data.get('id')
        id_ipress = data.get('idipress')
        ipress = db.session.query(IpressEssalud).filter_by(id_ipress=id_ipress).first()
        columna_nombre = MAPA_NIVEL.get(ipress.nivel_ipress)
        
        nuevo_estado = data.get('estado')
        # Validaciones básicas
        if not id_autoevaluacion or nuevo_estado not in [1, 2]:
            return jsonify({"success": False, "message": "Datos inválidos"}), 400

        registro = Autoevaluacion.query.get(id_autoevaluacion)
        if not registro:
            return jsonify({"success": False, "message": "Registro no encontrado"}), 404

        registro.estado = nuevo_estado
        db.session.commit()

        resultados = (
            db.session.query(
                Criterio.id_criterio,
                Criterio.codigo_criterio,
                func.count(CondicionCriterio.id_tecnica).label("total_requerido"),
                func.count(
                    case(
                        (CondicionCriterio.id_tecnica == 4, 1)
                    )
                ).label("total_tecnica_requerido_documentos"),
                func.count(
                    case(
                        (AutoevaluacionReporte.id_aereporte.is_(None),1)
                    )
                ).label("total_sin_reporte"),                
                func.count(
                    case(
                        (
                            and_(
                                Fuente.link_fuente.isnot(None),
                                func.length(Fuente.link_fuente) > 0
                            ),
                            1
                        ),
                        else_=None
                    )
                ).label("total_archivos_predefinidos") 
            )
            .outerjoin(CondicionCriterio, CondicionCriterio.id_criterio == Criterio.id_criterio)
            .outerjoin(Fuente,Fuente.id_condicion == CondicionCriterio.id_condicion)
            .outerjoin(AutoevaluacionReporte, and_(AutoevaluacionReporte.id_fuente == Fuente.id_fuente,AutoevaluacionReporte.id_autoevaluacion == id_autoevaluacion))
            .filter(Criterio.aplica_essalud == 1,getattr(Criterio, columna_nombre) == 1)
            .group_by(Criterio.id_criterio, Criterio.codigo_criterio)
        )
        ##print(resultados.statement.compile(compile_kwargs={"literal_binds": True}))
        resultados = resultados.all()

        insertados = []

        for r in resultados:
            
            puntaje_a_calificar = -1                
            """ #Si todas las fuentes son documentos y no he subido nada de archivos entonces puntaje = 0    
            if (r.total_requerido == r.total_tecnica_requerido_documentos) and  (r.total_tecnica_requerido_documentos == r.total_sin_reporte) and (r.total_archivos_predefinidos == 0):
                puntaje_a_calificar = 0
                
            #Si todas las fuentes que requiero son documentos y el total de documentos esta predefinido entonces puntaje = 2    
            if (r.total_requerido ==r.total_tecnica_requerido_documentos) and (r.total_tecnica_requerido_documentos==r.total_archivos_predefinidos):
                puntaje_a_calificar = 2
                
            if (r.total_requerido ==r.total_tecnica_requerido_documentos) and  (r.total_tecnica_requerido_documentos == r.total_sin_reporte)  and (r.total_archivos_predefinidos > 0):   
                puntaje_a_calificar = 1
             """    
            if (r.total_requerido == r.total_tecnica_requerido_documentos):
                if  (r.total_archivos_predefinidos > 0):
                    if (r.total_archivos_predefinidos == r.total_tecnica_requerido_documentos):
                        puntaje_a_calificar = 2
                    else:
                        puntaje_a_calificar = 1                   
                else: ##prefefinidos == 0
                    if (r.total_tecnica_requerido_documentos == r.total_sin_reporte):
                        puntaje_a_calificar = 0
            
            if r.codigo_criterio == 'EIF-1-5':
                print('EIF-1-5',r.codigo_criterio, puntaje_a_calificar)
                
                
            if puntaje_a_calificar > -1:
                existe = (
                    db.session.query(AutoevaluacionReporteCriterio)
                    .filter(AutoevaluacionReporteCriterio.id_autoevaluacion == id_autoevaluacion)
                    .filter(AutoevaluacionReporteCriterio.id_criterio == r.id_criterio)
                    .first()
                )

                if not existe:
                    nuevo = AutoevaluacionReporteCriterio(
                        id_autoevaluacion=id_autoevaluacion,
                        id_criterio=r.id_criterio,
                        puntaje_criterio=puntaje_a_calificar,
                        es_precalificado=False
                    )

                    db.session.add(nuevo)
                    insertados.append(r.id_criterio)

        db.session.commit()
        return jsonify({
            "success": True,
            "criterios_insertados": len(insertados),
            "ids_insertados": insertados
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    
    
     
#-----------------------------------------------------------------------------------
# API para calcular el porcentaje de avance en la calificacion de los criterios
#------------------------------------------------------------------------------------ 
@evaluacion_bp.route("/api/calculoavancecalificacionipress/<int:id_ipress>", methods=["GET"])
@login_required
def calculo_avance_calificacion_ipress(id_ipress):

    id_ipress = getattr(current_user, "id_ipress", None)
    id_anio_acreditacion = constants.ACREDITACION_ACTUAL

    # obtener id_autoevaluacion
    id_ae = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.id_ipress == id_ipress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .scalar()
    )

    if not id_ae:
        return jsonify({
            "total_criterios": 0,
            "total_calificados": 0,
            "porcentaje": 0
        })

    # obtener nivel de la ipress
    ipress = db.session.query(IpressEssalud).filter_by(id_ipress=id_ipress).first()
    columna_nombre = MAPA_NIVEL.get(ipress.nivel_ipress)
    columna_comparar = getattr(Criterio, columna_nombre)

    query  = (
        db.session.query(
            func.count(Criterio.id_criterio).label("total_criterios"),
            func.count(AutoevaluacionReporteCriterio.id_criterio).label("total_calificados")
        )
        .outerjoin(
            AutoevaluacionReporteCriterio,
            and_(
                AutoevaluacionReporteCriterio.id_criterio == Criterio.id_criterio,
                AutoevaluacionReporteCriterio.id_autoevaluacion == id_ae
            )
        )
        .filter(
            columna_comparar == 1,
            Criterio.aplica_essalud == 1
        )
    )
    resultado = query.first()
    total_criterios = resultado.total_criterios or 0
    total_calificados = resultado.total_calificados or 0
    porcentaje = 0
    if total_criterios > 0:
        porcentaje = round((total_calificados / total_criterios) * 100, 2)

    return jsonify({
        "total_criterios": total_criterios,
        "total_calificados": total_calificados,
        "porcentaje_avance_calificacion": porcentaje
    })
    

#-----------------------------------------------------------------------------------
# API para calcular el porcentaje de avance en el reporte de las fuentes
#------------------------------------------------------------------------------------ 
@evaluacion_bp.route("/api/calculoavancereportefuentes/<int:id_ipress>", methods=["GET"])
@login_required
def calculo_avance_reporte_fuentes(id_ipress):

    id_anio_acreditacion = constants.ACREDITACION_ACTUAL
    id_ae = (
        db.session.query(Autoevaluacion.id_autoevaluacion)
        .filter(Autoevaluacion.id_ipress == id_ipress)
        .filter(Autoevaluacion.periodo == id_anio_acreditacion)
        .scalar()
    )
    if not id_ae:
        return jsonify({
            "total_fuentes_requeridas": 0,
            "total_fuentes_reportadas": 0,
            "porcentaje": 0
        })

    ipress = db.session.query(IpressEssalud).filter_by(id_ipress=id_ipress).first()

    columna_nombre = MAPA_NIVEL.get(ipress.nivel_ipress)
    if not columna_nombre:
        return jsonify({
            "total_fuentes_requeridas": 0,
            "total_fuentes_reportadas": 0,
            "porcentaje": 0
        })

    columna_comparar = getattr(Criterio, columna_nombre)

    query = (
        db.session.query(
            func.count(Fuente.id_fuente).label("total_fuentes_requeridas"),
            func.count(AutoevaluacionReporte.id_fuente).label("total_fuentes_reportadas")
        )
        .outerjoin(
            AutoevaluacionReporte,
            and_(
                AutoevaluacionReporte.id_fuente == Fuente.id_fuente,
                AutoevaluacionReporte.id_autoevaluacion == id_ae
            )
        )
        .outerjoin(CondicionCriterio, CondicionCriterio.id_condicion == Fuente.id_condicion)
        .outerjoin(Criterio, Criterio.id_criterio == CondicionCriterio.id_criterio)
        .filter(
            Criterio.aplica_essalud == 1,
            columna_comparar == 1,
            or_(
                Fuente.link_fuente == None,
                Fuente.link_fuente == ''
            )
        )
    )

    resultado = query.first()

    total_fuentes_requeridas = resultado.total_fuentes_requeridas or 0
    total_fuentes_reportadas = resultado.total_fuentes_reportadas or 0

    porcentaje = 0
    if total_fuentes_requeridas > 0:
        porcentaje = round((total_fuentes_reportadas / total_fuentes_requeridas) * 100, 2)

    return jsonify({
        "total_fuentes_requeridas": total_fuentes_requeridas,
        "total_fuentes_reportadas": total_fuentes_reportadas,
        "porcentaje": porcentaje
    })
    
#-----------------------------------------------------------
#API para leer los tipos de observaciones 
#-----------------------------------------------------------
@evaluacion_bp.route("api/gettiposobservaciones", methods=["GET"])
@login_required
def get_tipos_observaciones():
    
    tipos = TipoObservacion.query.all()
    data = [
        {
            "id": t.id_tipo_observacion,
            "nombre": t.nombre_tipo_observacion
        }
        for t in tipos
    ]

    return jsonify(data)
    

       
#-----------------------------------------------------------------------
# Validar si el criterio califica a 0
#-----------------------------------------------------------------------
@evaluacion_bp.route('/validarpuntajecero/<int:id_criterio>/<int:id_autoevaluacion>', methods=['GET'])
@login_required
def validarpuntajecero(id_criterio, id_autoevaluacion):

    id_ipress = current_user.id_ipress
    ipress = db.session.query(IpressEssalud).filter_by(id_ipress=id_ipress).first()
    columna_nombre = MAPA_NIVEL.get(ipress.nivel_ipress)

    resultado = (
        db.session.query(
            Criterio.id_criterio,
            Criterio.codigo_criterio,
            func.count(CondicionCriterio.id_tecnica).label("total_requerido"),
            func.count(
                case(
                    (CondicionCriterio.id_tecnica == 4, 1)
                )
            ).label("total_tecnica_requerido_documentos"),
            func.count(
                case(
                    (
                        and_(
                            or_(Fuente.link_fuente == None, Fuente.link_fuente == ''),
                            AutoevaluacionReporte.id_aereporte == None
                        ),
                        1
                    )
                )
            ).label("total_sin_reporte")
        )
        .outerjoin(CondicionCriterio, CondicionCriterio.id_criterio == Criterio.id_criterio)
        .outerjoin(Fuente, Fuente.id_condicion == CondicionCriterio.id_condicion)
        .outerjoin(
            AutoevaluacionReporte,
            and_(
                AutoevaluacionReporte.id_fuente == Fuente.id_fuente,
                AutoevaluacionReporte.id_autoevaluacion == id_autoevaluacion
            )
        )
        .filter(
            Criterio.id_criterio == id_criterio,
            Criterio.aplica_essalud == 1,
            getattr(Criterio, columna_nombre) == 1
        )
        .group_by(Criterio.id_criterio, Criterio.codigo_criterio)
        .first()       
    )

    cumple = (
        resultado.total_requerido ==
        resultado.total_tecnica_requerido_documentos ==
        resultado.total_sin_reporte
    )

    return jsonify({"cumple": cumple})
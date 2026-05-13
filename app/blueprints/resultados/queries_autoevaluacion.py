from sqlalchemy.orm import aliased

from app import db
from app.constants import ACREDITACION_ACTUAL, MAPA_NIVEL
from app.models import (
    Autoevaluacion,
    AutoevaluacionReporte,
    AutoevaluacionReporteCriterio,
    CondicionCriterio,
    Criterio,
    Estandar,
    Fuente,
    IpressEssalud,
    Macroproceso,
    ProcesoInstitucional,
    RedEssalud,
    TecnicaEvaluacion,
)


def get_autoevaluacion_detalle_list(id_ipress, id_mp):
    query0 = (
        db.session.query(
            Autoevaluacion.id_autoevaluacion,
            IpressEssalud.nivel_ipress,
        )
        .select_from(Autoevaluacion)
        .join(IpressEssalud, IpressEssalud.id_ipress == Autoevaluacion.id_ipress)
        .filter(
            Autoevaluacion.id_ipress == id_ipress,
            Autoevaluacion.periodo == ACREDITACION_ACTUAL,
        )
    )
    resultado = query0.first()
    if not resultado:
        return []

    id_autoevaluacion = resultado[0]
    nivel_ipress = resultado[1]
    arc = aliased(AutoevaluacionReporteCriterio)
    ar = aliased(AutoevaluacionReporte)

    columna_nombre = MAPA_NIVEL.get(nivel_ipress)
    if not columna_nombre:
        return []
    columna_comparar = getattr(Criterio, columna_nombre)

    query = (
        db.session.query(
            RedEssalud.nombre_red,
            IpressEssalud.nombre_ipress,
            IpressEssalud.nivel_ipress,
            Macroproceso.codigo_macroproceso,
            (Macroproceso.codigo_macroproceso + " - " + Macroproceso.nombre_macroproceso).label(
                "nombre_mp"
            ),
            Estandar.codigo_estandar,
            Criterio.codigo_criterio,
            (Criterio.codigo_criterio + " - " + Criterio.nombre_criterio).label(
                "nombre_criterio"
            ),
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
            ar.link_reporte,
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
            (arc.id_criterio == Criterio.id_criterio)
            & (arc.id_autoevaluacion == Autoevaluacion.id_autoevaluacion),
        )
        .outerjoin(
            ar,
            (ar.id_fuente == Fuente.id_fuente)
            & (ar.id_autoevaluacion == Autoevaluacion.id_autoevaluacion),
        )
        .filter(
            Autoevaluacion.id_autoevaluacion == id_autoevaluacion,
            Criterio.aplica_essalud.is_(True),
        )
    )
    if columna_comparar is not None:
        query = query.filter(columna_comparar.is_(True))

    if id_mp is not None and id_mp != 0:
        query = query.filter(Macroproceso.id_macroproceso == id_mp)

    query = query.order_by(
        Macroproceso.id_macroproceso,
        Estandar.id_estandar,
        Criterio.id_criterio,
        CondicionCriterio.id_condicion,
    )
    result = query.all()
    return [dict(row._mapping) for row in result]

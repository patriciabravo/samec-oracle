from app.models import Macroproceso, Estandar, Criterio, IpressEssalud, AutoevaluacionReporteCriterio, Autoevaluacion
from app import db
from sqlalchemy import func, and_


ARR_MACROPROCESOS = [
    "DIR", "GRH", "GCA", "MRA", "GSD", "CGP",
    "ATA", "AEX", "ATH", "EMG", "ATQ", "DIV",
    "ADT", "ADA", "RCR", "GMD", "GIN", "DLD", "MRS", "NYD", "GIM", "EIF"
]

CATEGORIA_GER = ["DIR", "GRH", "GCA", "MRA", "GSD", "CGP"]
CATEGORIA_PRE = ["ATA", "AEX", "ATH", "EMG", "ATQ", "DIV"]
CATEGORIA_APO = ["ADT", "ADA", "RCR", "GMD", "GIN", "DLD", "MRS", "NYD", "GIM", "EIF"]

CONST_PORCENTAJE_MACROPROCESOS = {
    "DIR": 8, "GRH": 6, "GCA": 7, "MRA": 7, "GSD": 2, "CGP": 5,
    "ATA": 7, "AEX": 7, "ATH": 7, "EMG": 7, "ATQ": 7, "DIV": 5,
    "ADT": 2.5, "ADA": 2.5, "RCR": 2.5, "GMD": 2.5, "GIN": 2.5,
    "DLD": 2.5, "MRS": 2.5, "NYD": 2.5, "GIM": 2.5, "EIF": 2.5
}

MAPA_NIVEL = {
    "I-1": Criterio.nivel_i_1,
    "I-2": Criterio.nivel_i_2,
    "I-3": Criterio.nivel_i_3,
    "I-4": Criterio.nivel_i_4,
    "II-1": Criterio.nivel_ii_1,
    "II-2": Criterio.nivel_ii_2,
    "III-1": Criterio.nivel_iii_1
}


def obtener_datos_calculo(id_autoevaluacion, id_ipress):
    ipress = db.session.query(IpressEssalud).filter_by(id_ipress=id_ipress).first()
    if not ipress:
        return None

    autoevaluacion = db.session.query(Autoevaluacion).filter_by(
        id_autoevaluacion=id_autoevaluacion
    ).first()
    if not autoevaluacion:
        return None

    nivel_ipress_usuario = getattr(ipress, "nivel_ipress", None)
    columna_comparar = MAPA_NIVEL.get(nivel_ipress_usuario) or Criterio.nivel_i_3

    macros_db = db.session.query(
        Macroproceso.codigo_macroproceso,
        Macroproceso.nombre_macroproceso
    ).all()
    nombres_macroproceso = {m.codigo_macroproceso: m.nombre_macroproceso for m in macros_db}

    plantilla_macro = {
        "AA_puntaje_obtenido_por_tipo_macroproceso_proceso": 0,
        "AB_puntaje_obtenido_por_tipo_macroproceso_resultado": 0,
        "AD_ptje_max_proporcion_estructura": 0,
        "AE_ptje_max_proporcion_proceso": 0,
        "AF_ptje_max_proporcion_resultado": 0,
        "AH_ptje_obtenido_mp_estructura": 0,
        "AI_ptje_obtenido_mp_proceso": 0,
        "AJ_ptje_obtenido_mp_resultado": 0,
        "AK_sumatoria_puntaje_obtenido_mp_todos": 0,
        "AL_porcentaje_macroproceso_constante": 0,
        "AM_puntaje_min_por_macroproceso": 0,
        "AN_puntaje_obtenido_por_macroproceso": 0,
        "AO_cumplimiento_macroproceso": 0,
        "E_valor_estructura": 0, "F_valor_proceso": 0, "G_valor_resultado": 0,
        "H_cantidad_criterios_reportados": 0,
        "I_puntaje_maximo_estructura": 0, "J_puntaje_maximo_proceso": 0, "K_puntaje_maximo_resultado": 0,
        "L_sumatoria_total_pmt": 0,
        "Q_puntaje_maximo_estructura_peso": 0, "R_puntaje_maximo_proceso_peso": 0,
        "S_puntaje_maximo_resultado_peso": 0,
        "T_sumatoria_total": 0,
        "U_ptc_estructura_criterio": 0, "V_ptc_proceso_criterio": 0, "W_ptc_resultado_criterio": 0,
        "Z_puntaje_obtenido_por_tipo_macroproceso_estructura": 0
    }
    result = {}
    for macro in ARR_MACROPROCESOS:
        result[macro] = plantilla_macro.copy()
        result[macro]["macroproceso"] = macro

    query_total_cr = (
        db.session.query(
            Macroproceso.codigo_macroproceso,
            Criterio.tipo_criterio,
            func.count(Criterio.codigo_criterio).label('total_criterios')
        )
        .join(Estandar, Criterio.id_estandar == Estandar.id_estandar)
        .join(Macroproceso, Macroproceso.id_macroproceso == Estandar.id_macroproceso)
        .filter(columna_comparar == 1)
        .filter(Criterio.aplica_essalud == 1)
        .group_by(Macroproceso.id_macroproceso, Criterio.tipo_criterio)
        .order_by(Macroproceso.id_macroproceso, Criterio.tipo_criterio)
    )
    print(
        query_total_cr.statement.compile(
            compile_kwargs={"literal_binds": True}
        )
    )
    rows = query_total_cr.all()

    for macro, tipo, total in rows:
        if macro not in result:
            result[macro] = {
                "macroproceso": macro,
                "E_valor_estructura": 0, "F_valor_proceso": 0, "G_valor_resultado": 0,
                "I_puntaje_maximo_estructura": 0, "J_puntaje_maximo_proceso": 0,
                "K_puntaje_maximo_resultado": 0,
                "Q_puntaje_maximo_estructura_peso": 0, "R_puntaje_maximo_proceso_peso": 0,
                "S_puntaje_maximo_resultado_peso": 0
            }
        if tipo == "Estructura":
            result[macro]["E_valor_estructura"] = total
            result[macro]["I_puntaje_maximo_estructura"] = int(total) * 2
            result[macro]["Q_puntaje_maximo_estructura_peso"] = int(total) * 2
        elif tipo == "Proceso":
            result[macro]["F_valor_proceso"] = total
            result[macro]["J_puntaje_maximo_proceso"] = int(total) * 2
            result[macro]["R_puntaje_maximo_proceso_peso"] = int(total) * 2 * 2
        elif tipo == "Resultado":
            result[macro]["G_valor_resultado"] = total
            result[macro]["K_puntaje_maximo_resultado"] = int(total) * 2
            result[macro]["S_puntaje_maximo_resultado_peso"] = int(total) * 2 * 3

        result[macro]["H_cantidad_criterios_reportados"] = (
            result[macro].get("E_valor_estructura", 0) +
            result[macro].get("F_valor_proceso", 0) +
            result[macro].get("G_valor_resultado", 0)
        )
        result[macro]["L_sumatoria_total_pmt"] = (
            result[macro].get("I_puntaje_maximo_estructura", 0) +
            result[macro].get("J_puntaje_maximo_proceso", 0) +
            result[macro].get("K_puntaje_maximo_resultado", 0)
        )
        result[macro]["T_sumatoria_total"] = (
            result[macro].get("Q_puntaje_maximo_estructura_peso", 0) +
            result[macro].get("R_puntaje_maximo_proceso_peso", 0) +
            result[macro].get("S_puntaje_maximo_resultado_peso", 0)
        )

        if result[macro]["T_sumatoria_total"] == 0:
            result[macro]["U_ptc_estructura_criterio"] = 0
            result[macro]["V_ptc_proceso_criterio"] = 0
            result[macro]["W_ptc_resultado_criterio"] = 0
            continue

        result[macro]["U_ptc_estructura_criterio"] = round(
            result[macro]["Q_puntaje_maximo_estructura_peso"] / result[macro]["T_sumatoria_total"] * 100, 2
        )
        result[macro]["V_ptc_proceso_criterio"] = round(
            result[macro]["R_puntaje_maximo_proceso_peso"] / result[macro]["T_sumatoria_total"] * 100, 2
        )
        result[macro]["W_ptc_resultado_criterio"] = round(
            result[macro]["S_puntaje_maximo_resultado_peso"] / result[macro]["T_sumatoria_total"] * 100, 2
        )
        result[macro]["AD_ptje_max_proporcion_estructura"] = round(
            result[macro]["U_ptc_estructura_criterio"] * result[macro]["L_sumatoria_total_pmt"] / 100, 2
        )
        result[macro]["AE_ptje_max_proporcion_proceso"] = round(
            result[macro]["V_ptc_proceso_criterio"] * result[macro]["L_sumatoria_total_pmt"] / 100, 2
        )
        result[macro]["AF_ptje_max_proporcion_resultado"] = round(
            result[macro]["W_ptc_resultado_criterio"] * result[macro]["L_sumatoria_total_pmt"] / 100, 2
        )

    sumatoria_col_L_totales_pmt = sum(
        result.get(macro, {}).get("L_sumatoria_total_pmt", 0) for macro in ARR_MACROPROCESOS
    )

    query_mp = (
        db.session.query(
            Macroproceso.codigo_macroproceso.label("macroproceso"),
            Criterio.tipo_criterio.label("tipo_criterio"),
            func.coalesce(func.sum(AutoevaluacionReporteCriterio.puntaje_criterio), 0).label("puntaje_macroproceso")
        )
        .select_from(Criterio)
        .join(Estandar, Criterio.id_estandar == Estandar.id_estandar, isouter=True)
        .join(Macroproceso, Macroproceso.id_macroproceso == Estandar.id_macroproceso, isouter=True)
        .join(
            AutoevaluacionReporteCriterio,
            and_(
                AutoevaluacionReporteCriterio.id_criterio == Criterio.id_criterio,
                AutoevaluacionReporteCriterio.id_autoevaluacion == id_autoevaluacion
            ),
            isouter=True
        )
        .group_by(Macroproceso.id_macroproceso, Criterio.tipo_criterio)
        .order_by(Macroproceso.id_macroproceso, Criterio.tipo_criterio)
    )
    rows_mp = query_mp.all()

    for macro, tipo, puntaje in rows_mp:
        if puntaje is None:
            puntaje = 0
        if tipo == "Estructura":
            result[macro]["Z_puntaje_obtenido_por_tipo_macroproceso_estructura"] = puntaje
            if result.get(macro, {}).get("I_puntaje_maximo_estructura", 0) != 0:
                result[macro]["AH_ptje_obtenido_mp_estructura"] = round(
                    result[macro]["Z_puntaje_obtenido_por_tipo_macroproceso_estructura"] *
                    result[macro]["AD_ptje_max_proporcion_estructura"] /
                    result[macro]["I_puntaje_maximo_estructura"], 2
                )
            else:
                result[macro]["AH_ptje_obtenido_mp_estructura"] = 0
        elif tipo == "Proceso":
            result[macro]["AA_puntaje_obtenido_por_tipo_macroproceso_proceso"] = puntaje
            if result.get(macro, {}).get("J_puntaje_maximo_proceso", 0) != 0:
                result[macro]["AI_ptje_obtenido_mp_proceso"] = round(
                    result[macro]["AA_puntaje_obtenido_por_tipo_macroproceso_proceso"] *
                    result[macro]["AE_ptje_max_proporcion_proceso"] /
                    result[macro]["J_puntaje_maximo_proceso"], 2
                )
            else:
                result[macro]["AI_ptje_obtenido_mp_proceso"] = 0
        elif tipo == "Resultado":
            result[macro]["AB_puntaje_obtenido_por_tipo_macroproceso_resultado"] = puntaje
            if result.get(macro, {}).get("K_puntaje_maximo_resultado", 0) != 0:
                result[macro]["AJ_ptje_obtenido_mp_resultado"] = round(
                    result[macro]["AB_puntaje_obtenido_por_tipo_macroproceso_resultado"] *
                    result[macro]["AF_ptje_max_proporcion_resultado"] /
                    result[macro]["K_puntaje_maximo_resultado"], 2
                )
            else:
                result[macro]["AJ_ptje_obtenido_mp_resultado"] = 0

    for macro, _, _ in rows_mp:
        if macro not in result:
            result[macro] = {}
        for key in ["Z_puntaje_obtenido_por_tipo_macroproceso_estructura",
                    "AA_puntaje_obtenido_por_tipo_macroproceso_proceso",
                    "AB_puntaje_obtenido_por_tipo_macroproceso_resultado",
                    "AH_ptje_obtenido_mp_estructura", "AI_ptje_obtenido_mp_proceso", "AJ_ptje_obtenido_mp_resultado"]:
            if key not in result[macro]:
                result[macro][key] = 0

    for macro, _, _ in rows_mp:
        result[macro]["AK_sumatoria_puntaje_obtenido_mp_todos"] = round(
            result[macro].get("AH_ptje_obtenido_mp_estructura", 0) +
            result[macro].get("AI_ptje_obtenido_mp_proceso", 0) +
            result[macro].get("AJ_ptje_obtenido_mp_resultado", 0), 2
        )

    for macro in ARR_MACROPROCESOS:
        result[macro]["AL_porcentaje_macroproceso_constante"] = CONST_PORCENTAJE_MACROPROCESOS.get(macro, 0)

    for macro in ARR_MACROPROCESOS:
        if result[macro].get("H_cantidad_criterios_reportados", 0) == 0:
            result[macro]["AM_puntaje_min_por_macroproceso"] = 0
        else:
            result[macro]["AM_puntaje_min_por_macroproceso"] = round(
                CONST_PORCENTAJE_MACROPROCESOS[macro] * sumatoria_col_L_totales_pmt / 100, 2
            )

    for macro in ARR_MACROPROCESOS:
        if result[macro].get("L_sumatoria_total_pmt", 0) == 0:
            result[macro]["AN_puntaje_obtenido_por_macroproceso"] = 0
        else:
            result[macro]["AN_puntaje_obtenido_por_macroproceso"] = round(
                (result[macro]["AK_sumatoria_puntaje_obtenido_mp_todos"] *
                 result[macro]["AM_puntaje_min_por_macroproceso"] /
                 result[macro]["L_sumatoria_total_pmt"]), 2
            )

    for macro in ARR_MACROPROCESOS:
        if result[macro].get("AM_puntaje_min_por_macroproceso", 0) == 0:
            result[macro]["AO_cumplimiento_macroproceso"] = 0
        else:
            result[macro]["AO_cumplimiento_macroproceso"] = round(
                (result[macro]["AN_puntaje_obtenido_por_macroproceso"] /
                 result[macro]["AM_puntaje_min_por_macroproceso"] * 100), 2
            )

    AQ_porcentajes_categorias = {"GER": 35, "PRE": 40, "APO": 25}
    AP_puntaje_max_categoria = {
        "GER": sum(result[m].get("AM_puntaje_min_por_macroproceso", 0) for m in CATEGORIA_GER if m in result),
        "PRE": sum(result[m].get("AM_puntaje_min_por_macroproceso", 0) for m in CATEGORIA_PRE if m in result),
        "APO": sum(result[m].get("AM_puntaje_min_por_macroproceso", 0) for m in CATEGORIA_APO if m in result)
    }
    AP_Total = AP_puntaje_max_categoria.get("GER", 0) + AP_puntaje_max_categoria.get("PRE", 0) + AP_puntaje_max_categoria.get("APO", 0)
    AR_puntaje_max_por_categoria_total = {
        "GER": AP_Total * AQ_porcentajes_categorias["GER"] / 100,
        "PRE": AP_Total * AQ_porcentajes_categorias["PRE"] / 100,
        "APO": AP_Total * AQ_porcentajes_categorias["APO"] / 100
    }
    AS_puntaje_obtenido_por_categoria = {
        "GER": sum(result[m].get("AN_puntaje_obtenido_por_macroproceso", 0) for m in CATEGORIA_GER if m in result),
        "PRE": sum(result[m].get("AN_puntaje_obtenido_por_macroproceso", 0) for m in CATEGORIA_PRE if m in result),
        "APO": sum(result[m].get("AN_puntaje_obtenido_por_macroproceso", 0) for m in CATEGORIA_APO if m in result)
    }
    AT_puntaje_obtenido_por_categoria = {}
    for cat in ["GER", "PRE", "APO"]:
        ap_cat = AP_puntaje_max_categoria.get(cat, 0)
        if ap_cat == 0:
            AT_puntaje_obtenido_por_categoria[cat] = 0
        else:
            AT_puntaje_obtenido_por_categoria[cat] = (
                AS_puntaje_obtenido_por_categoria[cat] *
                AR_puntaje_max_por_categoria_total[cat] / ap_cat
            )

    datos_categoria = [
        {"categoria": "GER", "AP_puntaje_max_categoria": AP_puntaje_max_categoria["GER"],
         "AQ_porcentaje_categoria": AQ_porcentajes_categorias["GER"],
         "AR_total_ptje_categoria_max": AR_puntaje_max_por_categoria_total["GER"],
         "AS_puntaje_max_categoria": AS_puntaje_obtenido_por_categoria["GER"],
         "AT_puntaje_obtenido": AT_puntaje_obtenido_por_categoria["GER"]},
        {"categoria": "PRE", "AP_puntaje_max_categoria": AP_puntaje_max_categoria["PRE"],
         "AQ_porcentaje_categoria": AQ_porcentajes_categorias["PRE"],
         "AR_total_ptje_categoria_max": AR_puntaje_max_por_categoria_total["PRE"],
         "AS_puntaje_max_categoria": AS_puntaje_obtenido_por_categoria["PRE"],
         "AT_puntaje_obtenido": AT_puntaje_obtenido_por_categoria["PRE"]},
        {"categoria": "APO", "AP_puntaje_max_categoria": AP_puntaje_max_categoria["APO"],
         "AQ_porcentaje_categoria": AQ_porcentajes_categorias["APO"],
         "AR_total_ptje_categoria_max": AR_puntaje_max_por_categoria_total["APO"],
         "AS_puntaje_max_categoria": AS_puntaje_obtenido_por_categoria["APO"],
         "AT_puntaje_obtenido": AT_puntaje_obtenido_por_categoria["APO"]}
    ]

    AR_total = sum(AR_puntaje_max_por_categoria_total.values())
    AT_total = sum(AT_puntaje_obtenido_por_categoria.values())
    porcentaje_final = (AT_total / AR_total * 100) if AR_total else 0

    tiene_datos = sumatoria_col_L_totales_pmt > 0

    return {
        "result": result,
        "datos_categoria": datos_categoria,
        "porcentaje_final": porcentaje_final,
        "sumatoria_col_L": sumatoria_col_L_totales_pmt,
        "ipress": ipress,
        "autoevaluacion": autoevaluacion,
        "nombres_macroproceso": nombres_macroproceso,
        "tiene_datos": tiene_datos,
    }

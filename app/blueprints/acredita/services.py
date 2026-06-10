from app import db
from flask_login import login_required, current_user
from collections import defaultdict
from app.models import ProcesoInstitucional, Criterio, CondicionCriterio, TecnicaEvaluacion

class AcreditaService:

    @staticmethod
    @login_required
    def listar_procesos():
        procesos = ProcesoInstitucional.query.order_by(
            ProcesoInstitucional.nombre_proceso
        ).all()

        return [
            {
                "id_proceso": p.id_proceso,
                "nombre_proceso": p.nombre_proceso
            }
            for p in procesos
        ]

    @staticmethod
    @login_required
    def obtener_criterio(id_criterio):
        resultado = (
            db.session.query(
                Criterio.id_criterio,
                Criterio.codigo_criterio,
                Criterio.nombre_criterio,
                Criterio.puntaje_0_txt,
                Criterio.puntaje_1_txt,
                Criterio.puntaje_2_txt,
                Criterio.aplica_essalud,
                Criterio.tipo_criterio,
                Criterio.nivel_i_1,
                Criterio.nivel_i_2,
                Criterio.nivel_i_3,
                Criterio.nivel_i_4,
                Criterio.nivel_ii_1,
                Criterio.nivel_ii_2,
                Criterio.nivel_iii_1,
                Criterio.id_proceso,
                ProcesoInstitucional.nombre_proceso
            )
            .outerjoin(ProcesoInstitucional,ProcesoInstitucional.id_proceso == Criterio.id_proceso)
            .filter(Criterio.id_criterio == id_criterio)
            .first()
        )
        if not resultado:
            return None
        return resultado._asdict()
    
    @staticmethod
    @login_required
    def crear_condicion(data):
        try:
            condicion = CondicionCriterio(
                id_criterio=data.get('id_criterio'),
                nombre_condicion=data.get('nombre_condicion'),
                puntaje_condicion=data.get('select_puntaje'),
                id_tecnica=data.get('select_tecnica'),
                normativa_condicion=data.get('normativa_condicion'),
                link_normativa=data.get('link_normativa'),
                tipo_condicion=data.get('tipo_condicion')
            )

            db.session.add(condicion)
            db.session.commit()

            return {
                'success': True,
                'mensaje': 'Condición registrada correctamente',
                'id_condicion': condicion.id_condicion
            }

        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'mensaje': str(e)
            }

    @staticmethod
    @login_required
    def actualizar_condicion(id_condicion, data):
        try:
            condicion = CondicionCriterio.query.get(id_condicion)
            if not condicion:
                return {
                    'success': False,
                    'mensaje': 'Condición no encontrada'
                }
            condicion.id_criterio = data.get('id_criterio')
            condicion.nombre_condicion = data.get('nombre_condicion')
            condicion.puntaje_condicion = data.get('select_puntaje')
            condicion.id_tecnica = data.get('select_tecnica')
            condicion.normativa_condicion = data.get('normativa_condicion')
            condicion.link_normativa = data.get('link_normativa')
            condicion.tipo_condicion = data.get('tipo_condicion')
            db.session.commit()
            return {
                'success': True,
                'mensaje': 'Condición actualizada correctamente'
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'mensaje': str(e)
            }

    def get_condicion_by_id(id_condicion):
        condicion = (
            db.session.query(
                CondicionCriterio.id_condicion,
                CondicionCriterio.nombre_condicion,
                CondicionCriterio.id_tecnica,
                TecnicaEvaluacion.nombre_tecnica,
                CondicionCriterio.puntaje_condicion,
                CondicionCriterio.normativa_condicion,
                CondicionCriterio.link_normativa,
                CondicionCriterio.id_criterio,
                CondicionCriterio.tipo_condicion
            )
            .outerjoin(TecnicaEvaluacion,TecnicaEvaluacion.id_tecnica == CondicionCriterio.id_tecnica)
            .filter(CondicionCriterio.id_condicion == id_condicion)
            .first()
        )
        if not condicion:
            return None
        return {
            "id_condicion": condicion.id_condicion,
            "nombre_condicion": condicion.nombre_condicion,
            "id_tecnica": condicion.id_tecnica,
            "nombre_tecnica": condicion.nombre_tecnica,
            "puntaje_condicion": condicion.puntaje_condicion,
            "normativa_condicion": condicion.normativa_condicion,
            "link_normativa": condicion.link_normativa,
            "id_criterio": condicion.id_criterio,
            "tipo_condicion": condicion.tipo_condicion,
        }
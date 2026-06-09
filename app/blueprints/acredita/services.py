from app import db
from flask_login import login_required, current_user
from collections import defaultdict
from app.models import ProcesoInstitucional, Criterio

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
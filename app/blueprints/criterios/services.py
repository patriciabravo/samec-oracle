from app import db
from flask_login import login_required, current_user
from collections import defaultdict
from app.models import ProcesoInstitucional, Criterio

class CriteriosService:
    @staticmethod
    @login_required
    def listar_criterios():
        criterios = (
            Criterio.query
            .outerjoin(ProcesoInstitucional,ProcesoInstitucional.id_proceso == Criterio.id_proceso)
            .add_columns(ProcesoInstitucional.nombre_proceso)
            .order_by(Criterio.id_criterio)
            .all()
        )        
        return [
            {
                "id_criterio": criterio.id_criterio,
                "codigo_criterio": criterio.codigo_criterio,
                "nombre_criterio": criterio.nombre_criterio,
                "puntaje_0_txt": criterio.puntaje_0_txt,
                "puntaje_1_txt": criterio.puntaje_1_txt,
                "puntaje_2_txt": criterio.puntaje_2_txt,
                "aplica_essalud": criterio.aplica_essalud,
                "tipo_criterio": criterio.tipo_criterio,
                "id_proceso": criterio.id_proceso,
                "nombre_proceso": nombre_proceso
            }
            for criterio, nombre_proceso in criterios
        ]

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
    def actualizar_criterio(id_criterio, data):
        criterio = Criterio.query.get(id_criterio)
        if not criterio:
            return None
        criterio.codigo_criterio = data.get("codigo_criterio", criterio.codigo_criterio)
        criterio.nombre_criterio = data.get("nombre_criterio", criterio.nombre_criterio)
        criterio.puntaje_0_txt = data.get("puntaje_0", criterio.puntaje_0_txt)
        criterio.puntaje_1_txt = data.get("puntaje_1", criterio.puntaje_1_txt)
        criterio.puntaje_2_txt = data.get("puntaje_2", criterio.puntaje_2_txt)
        criterio.aplica_essalud = data.get("sel_aplica_essalud", criterio.aplica_essalud)
        criterio.tipo_criterio = data.get("sel_tipo_criterio", criterio.tipo_criterio)
        criterio.nivel_i_1 = data.get("sel_nivel_I_1", criterio.nivel_i_1)
        criterio.nivel_i_2 = data.get("sel_nivel_I_2", criterio.nivel_i_2)
        criterio.nivel_i_3 = data.get("sel_nivel_I_3", criterio.nivel_i_3)
        criterio.nivel_i_4 = data.get("sel_nivel_I_4", criterio.nivel_i_4)
        criterio.nivel_ii_1 = data.get("sel_nivel_II_1", criterio.nivel_ii_1)
        criterio.nivel_ii_2 = data.get("sel_nivel_II_2", criterio.nivel_ii_2)
        criterio.nivel_iii_1 = data.get("sel_nivel_III_1", criterio.nivel_iii_1)
        criterio.id_proceso = data.get("sel_procesoinstitucional", criterio.id_proceso)
        db.session.commit()
        return {
            "success": True,
            "message": "Criterio actualizado correctamente"
        }
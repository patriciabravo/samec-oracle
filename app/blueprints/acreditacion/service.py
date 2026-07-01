from app import db
from app.models import AcreditacionH1EquipoAcreditacion

class AcreditacionHitoService:

    @staticmethod
    def guardar_hito_1(id_acreditacion, form):
        nombres = form.getlist("miembro_nombre[]")
        cargos = form.getlist("miembro_cargo[]")
        lideres = form.getlist("miembro_lider[]")

        AcreditacionH1EquipoAcreditacion.query.filter_by(
            id_acreditacion=id_acreditacion
        ).delete()

        for nombre, cargo, lider in zip(nombres, cargos, lideres):
            nombre = nombre.strip()
            cargo = cargo.strip()

            if not nombre or not cargo:
                continue

            registro = AcreditacionH1EquipoAcreditacion(
                id_acreditacion=id_acreditacion,
                nombre_miembro=nombre,
                cargo_miembro=cargo,
                es_lider=int(lider)
            )
            db.session.add(registro)
        db.session.commit()
        
    @staticmethod
    def obtener_hito_1(id_acreditacion):
        miembros = (
            AcreditacionH1EquipoAcreditacion.query
            .filter_by(id_acreditacion=id_acreditacion)
            .order_by(AcreditacionH1EquipoAcreditacion.id_hito1)
            .all()
        )
        return [
            {
                "id_hito1": m.id_hito1,
                "nombre_miembro": m.nombre_miembro,
                "cargo_miembro": m.cargo_miembro,
                "es_lider": m.es_lider
            }
            for m in miembros
        ]
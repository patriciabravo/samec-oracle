from app import db
from app.models import AcreditacionH1EquipoAcreditacion

class AcreditacionHitoService:

    @staticmethod
    def guardar_hito_1(id_acreditacion, form):

        data = {}
        for key, value in form.items():
            if "[" in key and "]" in key:
                base = key.split("[")[0]
                index = key.split("[")[1].replace("]", "")
                if index not in data:
                    data[index] = {}
                data[index][base] = value

        AcreditacionH1EquipoAcreditacion.query.filter_by(
            id_acreditacion=id_acreditacion
        ).delete()
        
        print('data',data)
        
        for item in data.values():
            nombre = item.get("miembro_nombre", "").strip()
            cargo = item.get("miembro_cargo", "").strip()
            es_lider = item.get("miembro_lider", 0)
            if not nombre or not cargo:
                continue

            registro = AcreditacionH1EquipoAcreditacion(
                id_acreditacion=id_acreditacion,
                nombre_miembro=nombre,
                cargo_miembro=cargo,
                es_lider=es_lider
            )
            print(id_acreditacion,nombre,cargo,es_lider)
            db.session.add(registro)

        db.session.commit()
from app import db
from app.models import RedEssalud, Macrorregion
from flask_login import login_required


class RedService:

    @staticmethod
    @login_required
    def listar_redes():      
        redes = db.session.query(
            RedEssalud.id_red,
            RedEssalud.codigo_red,
            RedEssalud.nombre_red,
            Macrorregion.nombre_macrorregion
        ).join(
            Macrorregion,
            RedEssalud.macrorregion == Macrorregion.id_macroregion
        ).all()
        print(redes)
               
        return [
            {
                "id_red": red.id_red,
                "codigo_red": red.codigo_red,
                "nombre_red": red.nombre_red,
                "macrorregion": red.nombre_macrorregion
            }
            for red in redes
        ]

    @staticmethod
    def obtener_red(id_red):

        red = RedEssalud.query.get(id_red)

        if not red:
            return None

        return {
            "id_red": red.id_red,
            "codigo_red": red.codigo_red,
            "nombre_red": red.nombre_red,
            "macrorregion": red.macrorregion
        }

    @staticmethod
    def crear_red(data):

        nueva_red = RedEssalud(
            codigo_red=data.get('codigo_red'),
            nombre_red=data.get('nombre_red'),
            macrorregion=data.get('macrorregion')
        )

        db.session.add(nueva_red)
        db.session.commit()

        return {
            "message": "Red creada correctamente",
            "id_red": nueva_red.id_red
        }

    @staticmethod
    def actualizar_red(id_red, data):

        red = RedEssalud.query.get(id_red)

        if not red:
            return None

        red.codigo_red = data.get('codigo_red')
        red.nombre_red = data.get('nombre_red')
        red.macrorregion = data.get('macrorregion')

        db.session.commit()

        return {
            "message": "Red actualizada correctamente"
        }

    @staticmethod
    def eliminar_red(id_red):

        red = RedEssalud.query.get(id_red)

        if not red:
            return None

        db.session.delete(red)
        db.session.commit()

        return True
from app import db
from app.models import Macrorregion

def obtener_macrorregiones_service():
    results = (
        db.session.query(
            Macrorregion.id_macroregion,
            Macrorregion.nombre_macrorregion
        )
        .order_by(Macrorregion.nombre_macrorregion)
        .all()
    )
    return [
        {
            "id_macrorregion": row.id_macroregion,
            "nombre_macrorregion": row.nombre_macrorregion
        }
        for row in results
    ]
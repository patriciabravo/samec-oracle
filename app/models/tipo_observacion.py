from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.extensions import db

class TipoObservacion(db.Model):
    __tablename__ = "tipo_observacion"

    id_tipo_observacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_tipo_observacion: Mapped[str] = mapped_column(String(300), nullable=False)

    def __repr__(self) -> str:
        return f"<TipoObservacion {self.tipo_observacion}>"

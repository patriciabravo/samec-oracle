from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Sequence
from app.extensions import db

class TipoObservacion(db.Model):
    __tablename__ = "tipo_observacion"
    # Oracle recomienda Sequence
    id_tipo_observacion: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_tipo_observacion'),
        primary_key=True
    )
    nombre_tipo_observacion: Mapped[str] = mapped_column(
        String(300),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<TipoObservacion {self.id_tipo_observacion}>"
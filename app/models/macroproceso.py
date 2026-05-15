from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Sequence
from app.extensions import db

class Macroproceso(db.Model):
    __tablename__ = "macroproceso"
    # Oracle recomienda Sequence
    id_macroproceso: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_macroproceso'),
        primary_key=True
    )
    codigo_macroproceso: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )
    nombre_macroproceso: Mapped[str] = mapped_column(
        String(300),
        nullable=False
    )
    categoria_macroproceso: Mapped[str] = mapped_column(
        String(4),
        nullable=True
    )
    cantidad_estandares: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    criterios_evaluacion: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<Macroproceso {self.nombre_macroproceso}>"
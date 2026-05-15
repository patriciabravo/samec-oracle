from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Sequence
from app.extensions import db

class TecnicaEvaluacion(db.Model):
    __tablename__ = "tecnica_evaluacion"
    # Oracle recomienda Sequence
    id_tecnica: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_tecnica_evaluacion'),
        primary_key=True
    )
    nombre_tecnica: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    link_tecnica: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<TecnicaEvaluacion {self.nombre_tecnica}>"
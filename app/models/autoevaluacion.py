from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, Numeric, Sequence
from decimal import Decimal
from app.extensions import db

class Autoevaluacion(db.Model):
    __tablename__ = "autoevaluacion"
    # Oracle recomienda Sequence
    id_autoevaluacion: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_autoevaluacion'),
        primary_key=True
    )
    periodo: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    # Foránea a IPRESS
    id_ipress: Mapped[int] = mapped_column(
        ForeignKey("ipress_essalud.id_ipress", ondelete="CASCADE"),
        nullable=False
    )
    estado: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    puntaje_obtenido: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<Autoevaluacion {self.id_autoevaluacion}>"
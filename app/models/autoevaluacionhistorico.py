from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Numeric
from decimal import Decimal
from app.extensions import db

class AutoevaluacionHistorico(db.Model):
    __tablename__ = "autoevaluacion_historico"

    id_autoevaluacion_historico: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    red: Mapped[str] = mapped_column(String(150), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    nivel: Mapped[str] = mapped_column(String(50), nullable=False)
    ipress: Mapped[str] = mapped_column(String(150), nullable=False)

    puntaje_autoevaluacion: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)
    calificacion_autoevaluacion: Mapped[str] = mapped_column(String(50), nullable=True)

    puntaje_evaluacion_externa: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)
    calificacion_evaluacion_externa: Mapped[str] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        UniqueConstraint('ipress', 'anio', name='uq_ipress_anio'),
    )

    def __repr__(self) -> str:
        return f"<AutoevaluacionHistorico {self.ipress} - {self.anio}>"
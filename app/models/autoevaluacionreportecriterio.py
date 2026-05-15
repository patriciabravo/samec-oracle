from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, Sequence
from app.extensions import db

class AutoevaluacionReporteCriterio(db.Model):
    __tablename__ = "autoevaluacion_reporte_criterio"
    # Oracle recomienda PK simple con Sequence
    id: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_autoeval_reporte_criterio'),
        primary_key=True
    )
    id_autoevaluacion: Mapped[int] = mapped_column(
        ForeignKey(
            "autoevaluacion.id_autoevaluacion",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    id_criterio: Mapped[int] = mapped_column(
        ForeignKey(
            "criterio.id_criterio",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    puntaje_criterio: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    # Oracle no maneja BOOLEAN real
    # 1 = True
    # 0 = False
    es_precalificado: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<Autoevaluacion "
            f"{self.id_autoevaluacion} - "
            f"Criterio {self.id_criterio}>"
        )
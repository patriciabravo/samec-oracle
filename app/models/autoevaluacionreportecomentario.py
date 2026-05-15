from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, Sequence
from app.extensions import db

class AutoevaluacionReporteComentario(db.Model):
    __tablename__ = "autoevaluacion_reporte_comentario"
    # Oracle recomienda PK simple con Sequence
    id: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_autoeval_reporte_com'),
        primary_key=True
    )
    id_autoevaluacion: Mapped[int] = mapped_column(
        ForeignKey(
            "autoevaluacion.id_autoevaluacion",
            ondelete="SET NULL"
        ),
        nullable=True
    )
    id_fuente: Mapped[int] = mapped_column(
        ForeignKey(
            "fuente.id_fuente",
            ondelete="SET NULL"
        ),
        nullable=True
    )
    es_observado: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    observacion_fuente: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<AutoevaluacionReporteComentario "
            f"{self.id_autoevaluacion}>"
        )
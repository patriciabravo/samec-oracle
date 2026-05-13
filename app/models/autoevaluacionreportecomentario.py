from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from app.extensions import db

class AutoevaluacionReporteComentario(db.Model):
    __tablename__ = "autoevaluacion_reporte_comentario"

    id_autoevaluacion: Mapped[int] = mapped_column(
        ForeignKey("autoevaluacion.id_autoevaluacion", ondelete="SET NULL"),
        primary_key=True
    )

    id_fuente: Mapped[int] = mapped_column(
        ForeignKey("fuente.id_fuente", ondelete="SET NULL"),
        primary_key=True
    )
    es_observado: Mapped[int] = mapped_column(Integer, nullable=True)
    observacion_fuente: Mapped[int] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<AutoevaluacionReporteComentario {self.id_autoevaluacion}"

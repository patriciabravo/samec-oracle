from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from app.extensions import db

class AutoevaluacionComentarioTecnica(db.Model):
    __tablename__ = "autoevaluacion_comentario_tecnica"

    id_autoevaluacion: Mapped[int] = mapped_column(
        ForeignKey("autoevaluacion.id_autoevaluacion", ondelete="SET NULL"),
        primary_key=True
    )

    id_condicion: Mapped[int] = mapped_column(
        ForeignKey("condicion_criterio.id_condicion", ondelete="SET NULL"),
        primary_key=True
    )
    es_observado: Mapped[int] = mapped_column(Integer, nullable=False)
    comentario: Mapped[str] = mapped_column(String(800), nullable=True)

    def __repr__(self) -> str:
        return f"<AutoevaluacionComentarioTecnica {self.id_autoevaluacion}"

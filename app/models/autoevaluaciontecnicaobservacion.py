from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Sequence
from app.extensions import db

class AutoevaluacionTecnicaObservacion(db.Model):
    __tablename__ = "autoevaluacion_tecnica_observacion"
    # Oracle recomienda Sequence
    id: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_autoeval_tecnica_obs'),
        primary_key=True
    )
    id_autoevaluacion: Mapped[int] = mapped_column(
        ForeignKey("autoevaluacion.id_autoevaluacion", ondelete="CASCADE"),
        nullable=False
    )
    id_condicion: Mapped[int] = mapped_column(
        ForeignKey("condicion_criterio.id_condicion", ondelete="CASCADE"),
        nullable=False
    )
    nombre_archivo: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )
    ruta_archivo: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<AutoevaluacionTecnicaObservacion "
            f"{self.id_autoevaluacion} - "
            f"Condicion {self.id_condicion}>"
        )
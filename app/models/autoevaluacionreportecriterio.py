from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Boolean
from app.extensions import db

class AutoevaluacionReporteCriterio(db.Model):
    __tablename__ = "autoevaluacion_reporte_criterio"

    id_autoevaluacion: Mapped[int] = mapped_column(
        ForeignKey("autoevaluacion.id_autoevaluacion", ondelete="CASCADE"),
        primary_key=True
    )

    id_criterio: Mapped[int] = mapped_column(
        ForeignKey("criterio.id_criterio", ondelete="CASCADE"),
        primary_key=True
    )
    puntaje_criterio: Mapped[int] = mapped_column(Integer, nullable=True)    
    es_precalificado: Mapped[bool] = mapped_column(Boolean, nullable= True)

    def __repr__(self) -> str:
        return f"<Autoevaluacion {self.id_autoevaluacion} - Criterio {self.id_criterio}>"

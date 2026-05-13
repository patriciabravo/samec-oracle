from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Boolean
from app.extensions import db

class AutoevaluacionTecnicaObservacion(db.Model):
    __tablename__ = "autoevaluacion_tecnica_observacion"
    
    id = db.Column(db.Integer, primary_key=True) 

    id_autoevaluacion: Mapped[int] = mapped_column(
        ForeignKey("autoevaluacion.id_autoevaluacion", ondelete="CASCADE"),
        primary_key=True
    )
    
    id_condicion: Mapped[int] = mapped_column(
        ForeignKey("condicion_criterio.id_condicion", ondelete="CASCADE"),
        primary_key=True
    )

    nombre_archivo: Mapped[str] = mapped_column(String(500), nullable=True)
    ruta_archivo: Mapped[str] = mapped_column(String(500), nullable=True)
    
    def __repr__(self) -> str:
        return f"<AutoevaluacionTecnicaObservacion {self.id_autoevaluacion} - Criterio {self.id_condicion}>"
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from app.extensions import db

class AutoevaluacionReporte(db.Model):
    __tablename__ = "autoevaluacion_reporte"

    id_aereporte: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    #Foranea a evaluacion
    id_autoevaluacion: Mapped[int] = mapped_column(ForeignKey("autoevaluacion.id_autoevaluacion", ondelete="CASCADE"), nullable=False)
    #Foranea a criterio
    id_criterio: Mapped[int] = mapped_column(ForeignKey("criterio.id_criterio", ondelete="CASCADE"), nullable=False)
    #Foranea a condicion
    id_condicion: Mapped[int] = mapped_column(ForeignKey("condicion_criterio.id_condicion", ondelete="CASCADE"), nullable=False)
    #Foranea a fuente
    id_fuente: Mapped[int] = mapped_column(ForeignKey("fuente.id_fuente", ondelete="CASCADE"), nullable=False)
    #Foranea a tipo reporte
    id_tiporeporte: Mapped[int] = mapped_column(ForeignKey("tipo_reporte.id_tiporeporte", ondelete="CASCADE"), nullable=False)
    nombre_archivo: Mapped[str] = mapped_column(String(500), nullable=True)
    ruta_archivo: Mapped[str] = mapped_column(String(500), nullable=True)
    link_reporte: Mapped[str] = mapped_column(String(1000), nullable=True)
    puntaje_reporte: Mapped[int] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<AutoevaluacionReporte {self.id_aereporte}>"
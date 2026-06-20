from sqlalchemy import Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import db

class AcreditacionReporteHitos(db.Model):
    __tablename__ = "acreditacion_reporte_hitos"

    id_reporte_hito: Mapped[int] = mapped_column(
        Integer,
        Sequence("seq_acreditacion_reporte_hitos"),
        primary_key=True
    )
    id_autoevaluacion: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("autoevaluacion.id_autoevaluacion"),
        nullable=False
    )
    h1: Mapped[int] = mapped_column(Integer, nullable=True)
    h2: Mapped[int] = mapped_column(Integer, nullable=True)
    h3: Mapped[int] = mapped_column(Integer, nullable=True)
    h4: Mapped[int] = mapped_column(Integer, nullable=True)
    h5: Mapped[int] = mapped_column(Integer, nullable=True)
    h6: Mapped[int] = mapped_column(Integer, nullable=True)
    h7: Mapped[int] = mapped_column(Integer, nullable=True)
    h8: Mapped[int] = mapped_column(Integer, nullable=True)
    estado_acreditacion: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
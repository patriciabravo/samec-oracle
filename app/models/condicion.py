from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Sequence
from app.extensions import db


class CondicionCriterio(db.Model):
    __tablename__ = "condicion_criterio"
    # Oracle recomienda Sequence
    id_condicion: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_condicion_criterio'),
        primary_key=True
    )
    nombre_condicion: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    puntaje_condicion: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    normativa_condicion: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )
    link_normativa: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )
    tipo_condicion: Mapped[str] = mapped_column(
        String(5),
        nullable=True
    )
    # Foránea a técnica
    id_tecnica: Mapped[int] = mapped_column(
        ForeignKey("tecnica_evaluacion.id_tecnica", ondelete="CASCADE"),
        nullable=False
    )
    # Foránea a criterio
    # (el proceso institucional se obtiene vía Criterio.id_proceso)
    id_criterio: Mapped[int] = mapped_column(
        ForeignKey("criterio.id_criterio", ondelete="CASCADE"),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<CondicionCriterio {self.id_condicion}>"
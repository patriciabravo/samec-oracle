from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Sequence
from app.extensions import db

class AcreditacionH1EquipoAcreditacion(db.Model):
    __tablename__ = "acreditacion_h1_equipo_acreditacion"

    id_hito1: Mapped[int] = mapped_column(
        Integer,
        Sequence("seq_acreditacion_h1_miembro"),
        primary_key=True
    )
    id_acreditacion: Mapped[int] = mapped_column(
        ForeignKey(
            "autoevaluacion.id_autoevaluacion",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    nombre_miembro: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    cargo_miembro: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    es_lider: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    def __repr__(self) -> str:
        return (
            f"<AcreditacionH1EquipoAcreditacion "
            f"{self.id_miembro} - {self.nombre_miembro}>"
        )
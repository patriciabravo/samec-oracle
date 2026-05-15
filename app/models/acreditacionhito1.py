from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Sequence
from app.extensions import db

class AcreditacionHito1(db.Model):
    __tablename__ = "acreditacion_hito_1"
    # Oracle recomienda Sequence
    id_acreditacion_hito_1: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_acreditacion_hito_1'),
        primary_key=True
    )
    id_autoevaluacion: Mapped[int] = mapped_column(
        ForeignKey(
            "autoevaluacion.id_autoevaluacion",
            ondelete="CASCADE"
        ),
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    cargo: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    # Oracle no maneja BOOLEAN real
    # 1 = responsable
    # 0 = no responsable
    es_responsable: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<AcreditacionHito1 "
            f"{self.id_acreditacion_hito_1}>"
        )
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Boolean
from app.extensions import db

class AcreditacionHito1(db.Model):
    __tablename__ = "acreditacion_hito_1"
    id_acreditacion_hito_1: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    id_autoevaluacion: Mapped[int] = mapped_column(
        ForeignKey("autoevaluacion.id_autoevaluacion", ondelete="CASCADE"),
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
    es_responsable: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    def __repr__(self) -> str:
        return f"<AcreditacionHito1 {self.id_acreditacion_hito_1}>"
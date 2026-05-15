from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Sequence
from app.extensions import db

class Fuente(db.Model):
    __tablename__ = "fuente"
    # Oracle recomienda Sequence
    id_fuente: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_fuente'),
        primary_key=True
    )
    nombre_fuente: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    link_fuente: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )
    # Foránea a condición
    id_condicion: Mapped[int] = mapped_column(
        ForeignKey("condicion_criterio.id_condicion", ondelete="CASCADE"),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Fuente {self.nombre_fuente}>"
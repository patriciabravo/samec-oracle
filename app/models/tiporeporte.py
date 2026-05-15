from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Sequence
from app.extensions import db

class TipoReporte(db.Model):
    __tablename__ = "tipo_reporte"

    # Oracle recomienda Sequence
    id_tiporeporte: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_tipo_reporte'),
        primary_key=True
    )

    nombre_tiporeporte: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<TipoReporte {self.id_tiporeporte}>"
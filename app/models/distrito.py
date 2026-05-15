from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Sequence
from app.extensions import db

class Distrito(db.Model):
    __tablename__ = "distrito"
    # Oracle recomienda Sequence
    id_distrito: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_distrito'),
        primary_key=True
    )
    ubigeo_distrito: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True
    )
    distrito: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    # Foránea a provincia
    id_provincia: Mapped[int] = mapped_column(
        ForeignKey("provincia.id_provincia", ondelete="CASCADE"),
        nullable=False
    )
    superficie: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    altitud: Mapped[str] = mapped_column(
        String(20),
        nullable=True
    )
    latitud: Mapped[str] = mapped_column(
        String(20),
        nullable=True
    )
    longitud: Mapped[str] = mapped_column(
        String(20),
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<Distrito {self.distrito}>"

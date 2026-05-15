from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Sequence
from app.extensions import db

class Macrorregion(db.Model):
    __tablename__ = "macrorregion"
    # Oracle recomienda Sequence
    id_macroregion: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_macrorregion'),
        primary_key=True
    )
    nombre_macrorregion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    def __repr__(self) -> str:
        return f"<Macrorregion {self.nombre_macrorregion}>"
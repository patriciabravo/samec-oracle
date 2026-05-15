from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Sequence

from app.extensions import db


class Menu(db.Model):
    __tablename__ = "menu"

    # Oracle recomienda Sequence para autoincrement
    id_menu: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_menu'),
        primary_key=True
    )

    nombre_menu: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    icono_menu: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<Menu {self.nombre_menu}>"
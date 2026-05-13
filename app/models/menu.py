from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.extensions import db

class Menu(db.Model):
    __tablename__ = "menu"

    id_menu: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_menu: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    icono_menu: Mapped[str] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<Menu {self.nombre_menu}>"
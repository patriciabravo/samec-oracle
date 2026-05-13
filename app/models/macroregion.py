from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.extensions import db

class Macrorregion(db.Model):
    __tablename__ = "macrorregion"

    id_macroregion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_macrorregion: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    def __repr__(self) -> str:
        return f"<Menu {self.nombre_macrorregion}>"
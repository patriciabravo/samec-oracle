from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from app.extensions import db

class Distrito(db.Model):
    __tablename__ = "distrito"

    id_distrito: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ubigeo_distrito: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    distrito: Mapped[str] = mapped_column(String(100), nullable=False)
    #Foranea a departamento
    id_provincia: Mapped[int] = mapped_column(ForeignKey("provincia.id_provincia", ondelete="CASCADE"), nullable=False)
    superficie: Mapped[int] = mapped_column(Integer, nullable=True)
    altitud: Mapped[str] = mapped_column(String(20), nullable=True)
    latitud: Mapped[str] = mapped_column(String(20), nullable=True)
    longitud: Mapped[str] = mapped_column(String(20), nullable=True)

    def __repr__(self) -> str:
        return f"<Distrito {self.distrito}>"

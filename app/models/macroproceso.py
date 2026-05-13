from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.extensions import db

class Macroproceso(db.Model):
    __tablename__ = "macroproceso"

    id_macroproceso: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_macroproceso: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    nombre_macroproceso: Mapped[str] = mapped_column(String(300), nullable=False)
    categoria_macroproceso: Mapped[str] = mapped_column(String(4), nullable=True)
    cantidad_estandares: Mapped[int] = mapped_column(Integer, nullable=True)
    criterios_evaluacion: Mapped[int] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<Macroproceso {self.macroproceso}>"
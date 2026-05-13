from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.extensions import db

class TecnicaEvaluacion(db.Model):
    __tablename__ = "tecnica_evaluacion"

    id_tecnica: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_tecnica: Mapped[str] = mapped_column(String(500), nullable=False)
    link_tecnica: Mapped[str] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<TecnicaEvaluacion {self.nombre_tecnica}>"
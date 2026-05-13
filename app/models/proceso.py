from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.extensions import db

class ProcesoInstitucional(db.Model):
    __tablename__ = "proceso_institucional"

    id_proceso: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_proceso: Mapped[str] = mapped_column(String(200), nullable=False, unique=False)

    def __repr__(self) -> str:
        return f"<ProcesoInstitucional {self.id_proceso}>"
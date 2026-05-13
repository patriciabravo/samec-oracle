from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String,  ForeignKey
from app.extensions import db

class Provincia(db.Model):
    __tablename__ = "provincia"

    id_provincia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ubigeo_provincia: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    provincia: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    #Foranea a departamento
    id_departamento: Mapped[int] = mapped_column(ForeignKey("departamento.id_departamento", ondelete="CASCADE"), nullable=False)

    def __repr__(self) -> str:
        return f"<Provincia {self.provincia}>"
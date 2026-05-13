from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey
from app.extensions import db

class Estandar(db.Model):
    __tablename__ = "estandar"

    id_estandar: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_estandar: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre_estandar: Mapped[str] = mapped_column(String(500), nullable=False)
    #Foranea a macroproceso
    id_macroproceso: Mapped[int] = mapped_column(ForeignKey("macroproceso.id_macroproceso", ondelete="CASCADE"), nullable=False)

    def __repr__(self) -> str:
        return f"<Estandar {self.estandar}>"
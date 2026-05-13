from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Boolean
from app.extensions import db

class Fuente(db.Model):
    __tablename__ = "fuente"

    id_fuente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_fuente: Mapped[str] = mapped_column(String(500), nullable=False)
    link_fuente: Mapped[str] = mapped_column(String(500), nullable=True)
    #Foranea a condicion
    id_condicion: Mapped[int] = mapped_column(ForeignKey("condicion_criterio.id_condicion", ondelete="CASCADE"), nullable=False)

    def __repr__(self) -> str:
        return f"<Fuente {self.nombre_fuente}>"
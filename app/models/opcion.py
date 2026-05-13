from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey
from app.extensions import db

class Opcion(db.Model):
    __tablename__ = "opcion"

    id_opcion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_opcion: Mapped[str] = mapped_column(String(100), nullable=False)
    ruta_opcion: Mapped[str] = mapped_column(String(200), nullable=False)
    icono_opcion: Mapped[str] = mapped_column(String(100))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Clave foránea a Menu
    id_menu: Mapped[int] = mapped_column(ForeignKey("menu.id_menu", ondelete="CASCADE"), nullable=False)


    def __repr__(self) -> str:
        return f"<Opcion {self.nombre_opcion}>"
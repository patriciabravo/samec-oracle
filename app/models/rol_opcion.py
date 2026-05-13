from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from app import db

class RolOpcion(db.Model):
    __tablename__ = "rol_opcion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_rol: Mapped[int] = mapped_column(ForeignKey("rol.id_rol", ondelete="CASCADE"), nullable=False)
    id_opcion: Mapped[int] = mapped_column(ForeignKey("opcion.id_opcion", ondelete="CASCADE"), nullable=False)

    # Relaciones
    rol: Mapped["Rol"] = relationship("Rol", back_populates="opciones")
    def __repr__(self) -> str:
        return f"<RolOpcion rol={self.id_rol}, opcion={self.id_opcion}>"

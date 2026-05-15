from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, Sequence
from app import db
class RolOpcion(db.Model):
    __tablename__ = "rol_opcion"

    # Oracle recomienda Sequence
    id: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_rol_opcion'),
        primary_key=True
    )

    id_rol: Mapped[int] = mapped_column(
        ForeignKey("rol.id_rol", ondelete="CASCADE"),
        nullable=False
    )

    id_opcion: Mapped[int] = mapped_column(
        ForeignKey("opcion.id_opcion", ondelete="CASCADE"),
        nullable=False
    )

    # Relaciones
    rol: Mapped["Rol"] = relationship(
        "Rol",
        back_populates="opciones"
    )

    def __repr__(self) -> str:
        return f"<RolOpcion rol={self.id_rol}, opcion={self.id_opcion}>"

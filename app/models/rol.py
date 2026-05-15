from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Sequence
from app.extensions import db

class Rol(db.Model):
    __tablename__ = 'rol'

    # Oracle recomienda Sequence
    id_rol: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_rol'),
        primary_key=True
    )

    nombre_rol: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )

    descripcion_rol: Mapped[str] = mapped_column(
        String(200),
        nullable=True
    )

    # Relación con tabla intermedia
    usuarios: Mapped[list["RolUsuario"]] = relationship(
        "RolUsuario",
        back_populates="rol"
    )

    opciones: Mapped[list["RolOpcion"]] = relationship(
        "RolOpcion",
        back_populates="rol",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Rol {self.nombre_rol}>"
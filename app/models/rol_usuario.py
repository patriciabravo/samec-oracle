from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey, Sequence
from app.extensions import db

class RolUsuario(db.Model):
    __tablename__ = "rol_usuario"
    # Oracle recomienda Sequence
    id: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_rol_usuario'),
        primary_key=True
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False
    )
    id_rol: Mapped[int] = mapped_column(
        ForeignKey("rol.id_rol", ondelete="CASCADE"),
        nullable=False
    )
    fecha_asignacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )
    # Relaciones inversas
    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="roles_asociados"
    )
    rol: Mapped["Rol"] = relationship(
        "Rol",
        back_populates="usuarios"
    )

    def __repr__(self) -> str:
        return f"<RolUsuario usuario={self.id_usuario}, rol={self.id_rol}>"
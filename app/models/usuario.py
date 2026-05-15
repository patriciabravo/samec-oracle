from __future__ import annotations
from datetime import datetime
from typing import Optional
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text, Date, DateTime, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db
from app.models.ipress import IpressEssalud
from app.models.persona import Persona
from app.models.rol_usuario import RolUsuario

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    # Oracle recomienda usar Sequence
    id_usuario: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_usuario'),
        primary_key=True
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    password: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    correo: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False
    )
    # FK hacia persona.id_persona
    id_persona: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    # Oracle no maneja BOOLEAN real, 0 = inactivo, 1 = activo
    activo: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now
    )
    id_red: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    id_ipress: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ipress_essalud.id_ipress"),
        nullable=True
    )

    # Relación con Persona
    persona: Mapped[Optional["Persona"]] = relationship(
        "Persona",
        primaryjoin="foreign(Usuario.id_persona) == Persona.id_persona",
        back_populates="usuarios",
        viewonly=True,
        lazy="joined"
    )
    # Relación con IPRESS
    ipress: Mapped["IpressEssalud"] = relationship(
        backref="usuarios",
        lazy="joined"
    )
    # Relación con tabla intermedia
    roles_asociados: Mapped[list["RolUsuario"]] = relationship(
        "RolUsuario",
        back_populates="usuario"
    )
    # Relación con la tabla intermedia
    roles_asociados: Mapped[list["RolUsuario"]] = relationship("RolUsuario", back_populates="usuario")
   
    def get_id(self):
        return str(self.id_usuario)   # Flask-Login espera string
    
    def __repr__(self):
        return f"<Usuario {self.id_usuario}>"
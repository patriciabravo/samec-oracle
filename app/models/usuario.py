from __future__ import annotations
from datetime import datetime
from app.models.ipress import IpressEssalud
from app.models.persona import Persona
from app.models.rol_usuario import RolUsuario
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text, Date, DateTime
from app.extensions import db
from typing import Optional


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id_usuario: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(200), nullable=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    correo: Mapped[str] = mapped_column(unique=True, nullable=False)
    # FK hacia persona.id
    id_persona: Mapped[int] = mapped_column(Integer, nullable=True)   
    activo: Mapped[bool] = mapped_column(default=False, nullable=False)  #False=inactivo, True=activo
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, nullable=False,  default=datetime.now)    
    id_red: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    id_ipress: Mapped[int] = mapped_column(ForeignKey("ipress_essalud.id_ipress"), nullable=True)

    # Para acceder al atributo dentro de usuario puedes acceder a persona:  usuario.persona
    persona: Mapped[Optional["Persona"]] = relationship(
        "Persona",
        primaryjoin="foreign(Usuario.id_persona) == Persona.id_persona",
        back_populates="usuarios",
        viewonly=True,  # evita errores por no tener constraint real
        lazy="joined"
    )
    ipress: Mapped["IpressEssalud"] = relationship(backref="usuarios", lazy="joined")

    # Relación con la tabla intermedia
    roles_asociados: Mapped[list["RolUsuario"]] = relationship("RolUsuario", back_populates="usuario")
   
    def get_id(self):
        return str(self.id_usuario)   # Flask-Login espera string
    
    def __repr__(self):
        return f"<Usuario {self.id_usuario}>"
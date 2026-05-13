from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime
from app.extensions import db
from typing import List, Optional


class Persona(db.Model):
    __tablename__ = 'persona'

    id_persona: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_paterno: Mapped[str] = mapped_column(String(50), nullable=False)
    apellido_materno: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(20), nullable=False)
    numero_documento: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, nullable=False,  default=datetime.now)
    # Relación uno-a-muchos con Usuario
    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        primaryjoin="Persona.id_persona == foreign(Usuario.id_persona)",
        back_populates="persona",
        lazy="select"
    )
from __future__ import annotations
from datetime import datetime
from typing import List
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Sequence
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from app.extensions import db


class Persona(db.Model):
    __tablename__ = 'persona'

    # Oracle recomienda usar Sequence
    id_persona: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_persona'),
        primary_key=True
    )

    nombres: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    apellido_paterno: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    apellido_materno: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    tipo_documento: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    numero_documento: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now
    )

    # Relación uno-a-muchos con Usuario
    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        primaryjoin="Persona.id_persona == foreign(Usuario.id_persona)",
        back_populates="persona",
        lazy="select"
    )
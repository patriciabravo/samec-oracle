from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer
from app.extensions import db

class GestorRedes(db.Model):
    __tablename__ = 'gestor_redes'
    # Clave primaria compuesta
    id_usuario: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    id_red: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    def __repr__(self):
        return f"<GestorRedes id_usuario={self.id_usuario} id_red={self.id_red}>"
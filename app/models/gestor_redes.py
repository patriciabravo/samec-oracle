from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from app.extensions import db

class GestorRedes(db.Model):
    __tablename__ = 'gestor_redes'
    
    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    id_red: Mapped[int] = mapped_column(primary_key=True)
    
    def __repr__(self):
        return f"<GestorRedes id_usuario={self.id_usuario} id_red={self.id_red}>"
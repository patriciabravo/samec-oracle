from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime
from app.extensions import db

  
class IpressEssalud(db.Model):
    __tablename__ = 'ipress_essalud'

    id_ipress: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_ipress: Mapped[str] = mapped_column(String(10), nullable=False)
    nombre_ipress: Mapped[str] = mapped_column(String(200), nullable=False)
    nivel_ipress: Mapped[str] = mapped_column(String(10), nullable=False)
    tipo_ipress: Mapped[str] = mapped_column(String(10), nullable=False)

    #Clave foránea hacia RedEssalud
    id_red: Mapped[int] = mapped_column(ForeignKey("red_essalud.id_red"), nullable=False)

    #Clave foránea hacia Distrito
    id_distrito: Mapped[int] = mapped_column(ForeignKey("distrito.id_distrito"), nullable=False)

    # Relación inversa
    red: Mapped["RedEssalud"] = relationship(back_populates="ipresses")
    
    es_activo: Mapped[int] = mapped_column(Integer, nullable=True)
    

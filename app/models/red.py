from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime
from app.extensions import db

class RedEssalud(db.Model):
    __tablename__ = 'red_essalud'

    id_red: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_red: Mapped[str] = mapped_column(String(10), nullable=False)
    nombre_red: Mapped[str] = mapped_column(String(50), nullable=False)
    macrorregion: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relación con IpressEssalud (uno a muchos)
    ipresses: Mapped[list["IpressEssalud"]] = relationship(back_populates="red")

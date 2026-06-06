from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, String, Sequence

from app.extensions import db
from app.models.red import RedEssalud


class IpressEssalud(db.Model):
    __tablename__ = 'ipress_essalud'

    # Oracle recomienda Sequence
    id_ipress: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_ipress_essalud'),
        primary_key=True
    )

    codigo_ipress: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    nombre_ipress: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    nivel_ipress: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    tipo_ipress: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    # Clave foránea hacia RedEssalud
    id_red: Mapped[int] = mapped_column(
        ForeignKey("red_essalud.id_red"),
        nullable=False
    )

    # Clave foránea hacia Distrito
    id_distrito: Mapped[int] = mapped_column(
        ForeignKey("distrito.id_distrito"),
        nullable=False
    )

    # Relación inversa
    red: Mapped["RedEssalud"] = relationship(
        "RedEssalud",
        back_populates="ipresses"
    )

    # 1 = activo
    # 0 = inactivo
    es_activo: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<IpressEssalud {self.nombre_ipress}>"
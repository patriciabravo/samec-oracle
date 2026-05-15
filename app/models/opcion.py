from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Sequence
from app.extensions import db

class Opcion(db.Model):
    __tablename__ = "opcion"

    # Oracle recomienda Sequence
    id_opcion: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_opcion'),
        primary_key=True
    )

    nombre_opcion: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    ruta_opcion: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    icono_opcion: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    # Oracle no maneja BOOLEAN real
    # 1 = activo
    # 0 = inactivo
    activo: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    # Clave foránea a Menu
    id_menu: Mapped[int] = mapped_column(
        ForeignKey("menu.id_menu", ondelete="CASCADE"),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Opcion {self.nombre_opcion}>"
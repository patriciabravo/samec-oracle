from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Sequence
from app.extensions import db

class Criterio(db.Model):
    __tablename__ = "criterio"
    # Oracle recomienda Sequence
    id_criterio: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_criterio'),
        primary_key=True
    )
    codigo_criterio: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    nombre_criterio: Mapped[str] = mapped_column(
        String(800),
        nullable=False
    )
    puntaje_criterio: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    puntaje_0_txt: Mapped[str] = mapped_column(
        String(300),
        nullable=True
    )
    puntaje_1_txt: Mapped[str] = mapped_column(
        String(300),
        nullable=True
    )
    puntaje_2_txt: Mapped[str] = mapped_column(
        String(300),
        nullable=True
    )
    # Oracle no maneja BOOLEAN real
    # 1 = True
    # 0 = False
    aplica_essalud: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    tipo_criterio: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )
    nivel_i_1: Mapped[int] = mapped_column(Integer, nullable=True)
    nivel_i_2: Mapped[int] = mapped_column(Integer, nullable=True)
    nivel_i_3: Mapped[int] = mapped_column(Integer, nullable=True)
    nivel_i_4: Mapped[int] = mapped_column(Integer, nullable=True)
    nivel_ii_1: Mapped[int] = mapped_column(Integer, nullable=True)
    nivel_ii_2: Mapped[int] = mapped_column(Integer, nullable=True)
    nivel_iii_1: Mapped[int] = mapped_column(Integer, nullable=True)
    total_condiciones: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )
    # Foránea a estandar
    id_estandar: Mapped[int] = mapped_column(
        ForeignKey("estandar.id_estandar", ondelete="CASCADE"),
        nullable=False
    )
    # Foránea a proceso institucional
    id_proceso: Mapped[int] = mapped_column(
        ForeignKey("proceso_institucional.id_proceso", ondelete="CASCADE"),
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<Criterio {self.nombre_criterio}>"
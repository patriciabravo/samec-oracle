from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Boolean
from app.extensions import db

class Criterio(db.Model):
    __tablename__ = "criterio"

    id_criterio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_criterio: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre_criterio: Mapped[str] = mapped_column(String(800), nullable=False)
    puntaje_criterio: Mapped[str] = mapped_column(Integer, nullable=False)
    puntaje_0_txt: Mapped[str] = mapped_column(String(300))
    puntaje_1_txt: Mapped[str] = mapped_column(String(300))
    puntaje_2_txt: Mapped[str] = mapped_column(String(300))
    aplica_essalud: Mapped[bool] = mapped_column(Boolean)
    tipo_criterio: Mapped[str] = mapped_column(String(100))
    nivel_i_1: Mapped[bool] = mapped_column(Boolean)
    nivel_i_2: Mapped[bool] = mapped_column(Boolean)
    nivel_i_3: Mapped[bool] = mapped_column(Boolean)
    nivel_i_4: Mapped[bool] = mapped_column(Boolean)
    nivel_ii_1: Mapped[bool] = mapped_column(Boolean)
    nivel_ii_2: Mapped[bool] = mapped_column(Boolean)
    nivel_iii_1: Mapped[bool] = mapped_column(Boolean) 
    total_condiciones: Mapped[int] = mapped_column(Integer, nullable=True)
    #Foranea a estandar
    id_estandar: Mapped[int] = mapped_column(ForeignKey("estandar.id_estandar", ondelete="CASCADE"), nullable=False)
    #Foranea a proceso institucional
    id_proceso: Mapped[int] = mapped_column(ForeignKey("proceso_institucional.id_proceso", ondelete="CASCADE"), nullable=True)

    def __repr__(self) -> str:
        return f"<Criterio {self.criterio}>"
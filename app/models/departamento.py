from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Sequence
from app.extensions import db

class Departamento(db.Model):
    __tablename__ = "departamento"
    # Oracle recomienda Sequence
    id_departamento: Mapped[int] = mapped_column(
        Integer,
        Sequence('seq_departamento'),
        primary_key=True
    )

    departamento: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    def __repr__(self) -> str:
        return f"<Departamento {self.departamento}>"
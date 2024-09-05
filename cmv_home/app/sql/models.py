from sqlalchemy import Boolean, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base


class Admission(Base):
    __tablename__ = "admission"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    admission: Mapped[str] = mapped_column(DateTime)
    ambulatoire: Mapped[bool] = mapped_column(Boolean, default=True)
    sorti_le: Mapped[str] = mapped_column(DateTime, nullable=True)
    sortie_prevue_le: Mapped[str] = mapped_column(DateTime, nullable=True)


class Chambre(Base):
    __tablename__ = "chambre"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    numero: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    last_occuped: Mapped[str] = mapped_column(DateTime)
    last_freed: Mapped[str] = mapped_column(DateTime, nullable=True)
    last_cleanup: Mapped[str] = mapped_column(DateTime, nullable=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"))
    service: Mapped["Service"] = relationship("Service", back_populates="chambres")


class Patient(Base):
    __tablename__ = "patient"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    civilite: Mapped[str] = mapped_column(String, nullable=True)
    nom: Mapped[str] = mapped_column(String)
    prenom: Mapped[str] = mapped_column(String)


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nom: Mapped[str] = mapped_column(String, unique=True)
    chambres: Mapped[list["Chambre"]] = relationship(
        "Chambre", back_populates="service"
    )

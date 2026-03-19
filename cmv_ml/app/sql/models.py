"""
Modèles SQLAlchemy pour le service ML de prédiction.

Note : Les features médicales ont été ajoutées en tant que colonnes optionnelles.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..utils.database import Base


class Prediction(Base):
    """
    Modèle SQLAlchemy pour les prédictions validées.
    """

    __tablename__ = "prediction"

    id_prediction: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    prediction: Mapped[float] = mapped_column(Float, nullable=False)

    # Genre (0=F, 1=M)
    gender: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Comorbidités binaires (0/1)
    dialysisrenalendstage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    asthma: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    irondef: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pneum: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    substancedependence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    psychologicaldisordermajor: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    depress: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    psychother: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fibrosisandother: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    malnutrition: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hemo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Variables continues
    hematocrit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    neutrophils: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sodium: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    glucose: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bloodureanitro: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    creatinine: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bmi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pulse: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    respiration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Autres champs
    rcount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vdate: Mapped[datetime] = mapped_column(
        DateTime(), server_default=func.now(), nullable=True
    )
    discharged: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    lengthofstay: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    adid: Mapped[Optional[str]] = mapped_column(String, nullable=True)

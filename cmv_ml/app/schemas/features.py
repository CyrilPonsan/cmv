"""Schema de validation des features pour la prédiction de durée d'hospitalisation."""

import uuid
from typing import Literal, Optional

from pydantic import BaseModel, Field


class PredictionFeatures(BaseModel):
    """
    Schema de validation des 22 features pour la prédiction.

    Les features sont divisées en trois catégories:
    - Genre (binaire)
    - Comorbidités binaires (0/1)
    - Variables continues (valeurs positives)
    """

    # Metadatas
    adid: str
    id_prediction: Optional[uuid.UUID] | None = Field(default=None)

    # Genre (0=F, 1=M)
    gender: Literal[0, 1] = 0

    # Comorbidités binaires (0/1)
    dialysisrenalendstage: Literal[0, 1] = 0
    asthma: Literal[0, 1] = 0
    irondef: Literal[0, 1] = 0
    pneum: Literal[0, 1] = 0
    substancedependence: Literal[0, 1] = 0
    psychologicaldisordermajor: Literal[0, 1] = 0
    depress: Literal[0, 1] = 0
    psychother: Literal[0, 1] = 0
    fibrosisandother: Literal[0, 1] = 0
    malnutrition: Literal[0, 1] = 0
    hemo: Literal[0, 1] = 0

    # Variables continues (doivent être positives)
    hematocrit: Optional[float] = Field(default=None, gt=0)
    neutrophils: Optional[float] = Field(default=None, gt=0)
    sodium: Optional[float] = Field(default=None, gt=0)
    glucose: Optional[float] = Field(default=None, gt=0)
    bloodureanitro: Optional[float] = Field(default=None, gt=0)
    creatinine: Optional[float] = Field(default=None, gt=0)
    bmi: Optional[float] = Field(default=None, gt=0)
    pulse: Optional[int] = Field(default=None, gt=0)
    respiration: Optional[float] = Field(default=None, gt=0)

    # Autres champs
    rcount: Optional[int] = Field(default=0, ge=0)  # Nombre de visites précédentes
    prediction: Optional[float] = Field(
        default=None, ge=0
    )  # Durée prédite d'hospitalisation

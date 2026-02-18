"""Schema de validation des features pour la prédiction de durée d'hospitalisation."""

from typing import Literal

from pydantic import BaseModel, Field


class PredictionFeatures(BaseModel):
    """
    Schema de validation des 22 features pour la prédiction.
    
    Les features sont divisées en trois catégories:
    - Genre (binaire)
    - Comorbidités binaires (0/1)
    - Variables continues (valeurs positives)
    """

    # Genre (0=F, 1=M)
    gender: Literal[0, 1]

    # Comorbidités binaires (0/1)
    dialysisrenalendstage: Literal[0, 1]
    asthma: Literal[0, 1]
    irondef: Literal[0, 1]
    pneum: Literal[0, 1]
    substancedependence: Literal[0, 1]
    psychologicaldisordermajor: Literal[0, 1]
    depress: Literal[0, 1]
    psychother: Literal[0, 1]
    fibrosisandother: Literal[0, 1]
    malnutrition: Literal[0, 1]
    hemo: Literal[0, 1]

    # Variables continues (doivent être positives)
    hematocrit: float = Field(gt=0)
    neutrophils: float = Field(gt=0)
    sodium: float = Field(gt=0)
    glucose: float = Field(gt=0)
    bloodureanitro: float = Field(gt=0)
    creatinine: float = Field(gt=0)
    bmi: float = Field(gt=0)
    pulse: int = Field(gt=0)
    respiration: float = Field(gt=0)

    # Autres champs
    rcount: int = Field(ge=0)  # Nombre de visites précédentes
    secondarydiagnosisnonicd9: int = Field(ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "gender": 1,
                    "dialysisrenalendstage": 0,
                    "asthma": 0,
                    "irondef": 0,
                    "pneum": 0,
                    "substancedependence": 0,
                    "psychologicaldisordermajor": 0,
                    "depress": 0,
                    "psychother": 0,
                    "fibrosisandother": 0,
                    "malnutrition": 0,
                    "hemo": 0,
                    "hematocrit": 38.5,
                    "neutrophils": 65.0,
                    "sodium": 140.0,
                    "glucose": 100.0,
                    "bloodureanitro": 15.0,
                    "creatinine": 1.0,
                    "bmi": 25.0,
                    "pulse": 72,
                    "respiration": 16.0,
                    "rcount": 0,
                    "secondarydiagnosisnonicd9": 0,
                }
            ]
        }
    }

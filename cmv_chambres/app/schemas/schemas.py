# Import du module Pydantic pour la validation des données
from pydantic import BaseModel


# Modèle Pydantic pour représenter une réponse de succès avec message
class SuccessWithMessage(BaseModel):
    success: bool  # Indique si l'opération a réussi
    message: str  # Message descriptif du résultat de l'opération

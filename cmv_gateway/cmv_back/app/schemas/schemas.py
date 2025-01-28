from pydantic import BaseModel


# Modèle Pydantic pour les messages simples
class Message(BaseModel):
    # Le message à retourner
    message: str


# Modèle Pydantic pour les réponses avec succès et message
class SuccessWithMessage(BaseModel):
    # Indique si l'opération a réussi
    success: bool
    # Message descriptif du résultat
    message: str

from pydantic import BaseModel


# Modèle de réponse générique pour les opérations réussies
class SuccessWithMessage(BaseModel):
    # Indique si l'opération a réussi (True) ou échoué (False)
    success: bool
    # Message descriptif du résultat de l'opération
    message: str

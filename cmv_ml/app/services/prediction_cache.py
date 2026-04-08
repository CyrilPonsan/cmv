"""Cache en mémoire des prédictions en attente de validation."""

from datetime import datetime, timedelta, timezone
from uuid import UUID


class PredictionCache:
    """Cache en mémoire des prédictions en attente de validation.
    
    Stocke temporairement les prédictions générées pour permettre leur
    validation ultérieure sans re-soumettre les features médicales.
    Les entrées expirent automatiquement après le TTL configuré.
    """
    
    def __init__(self, ttl_minutes: int = 1):
        """Initialise le cache avec un TTL configurable.
        
        Args:
            ttl_minutes: Durée de vie des entrées en minutes (défaut: 30)
        """
        self._cache: dict[UUID, tuple[float, datetime]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
    
    def store(self, prediction_id: UUID, value: float) -> None:
        """Stocke une prédiction temporairement.
        
        Args:
            prediction_id: Identifiant unique de la prédiction
            value: Valeur prédite (durée d'hospitalisation en jours)
        """
        self._cache[prediction_id] = (value, datetime.now(timezone.utc))
    
    def get(self, prediction_id: UUID) -> float | None:
        """Récupère une prédiction si elle existe et n'est pas expirée.
        
        Args:
            prediction_id: Identifiant unique de la prédiction
            
        Returns:
            La valeur prédite si trouvée et non expirée, None sinon
        """
        if prediction_id not in self._cache:
            return None
        value, timestamp = self._cache[prediction_id]
        if datetime.now(timezone.utc) - timestamp > self._ttl:
            del self._cache[prediction_id]
            return None
        return value
    
    def remove(self, prediction_id: UUID) -> None:
        """Supprime une prédiction du cache.
        
        Args:
            prediction_id: Identifiant unique de la prédiction à supprimer
        """
        self._cache.pop(prediction_id, None)


# Instance singleton du cache pour l'application
prediction_cache = PredictionCache()

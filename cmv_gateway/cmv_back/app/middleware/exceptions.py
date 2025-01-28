# Import des modules nécessaires
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Import du logger personnalisé
from ..utils.logging_setup import LoggerSetup

# Initialisation du logger
logger = LoggerSetup()


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour gérer les exceptions de manière globale dans l'application.
    Capture toutes les exceptions non gérées et retourne une réponse JSON appropriée.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Méthode principale du middleware qui intercepte et traite les requêtes.

        Args:
            request (Request): La requête HTTP entrante
            call_next: La fonction pour passer au middleware suivant

        Returns:
            Response: La réponse HTTP, soit normale soit une erreur formatée en JSON
        """
        try:
            # Passage de la requête au middleware suivant
            return await call_next(request)
        except Exception as e:
            # Log de l'exception pour le debugging
            print("spotted regular exception")
            logger.write_debug(str(e))
            # Retourne une réponse d'erreur générique en JSON
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                },
            )

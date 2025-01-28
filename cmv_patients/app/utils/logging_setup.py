import logging
import logging.handlers

from fastapi import Request, HTTPException


class LoggerSetup:
    """Classe singleton pour configurer et gérer les logs de l'application"""

    _instance = None

    def __new__(cls):
        """Implémentation du pattern Singleton"""
        if cls._instance is None:
            cls._instance = super(LoggerSetup, cls).__new__(cls)
            cls._instance.setup_logging()
        return cls._instance

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        Fonction utilitaire pour récupérer l'adresse IP du client à partir de l'objet Request.
        Vérifie d'abord les headers X-Real-IP et X-Forwarded-For.
        """
        client_ip = request.headers.get("X-Real-IP") or request.headers.get(
            "X-Forwarded-For"
        )
        return client_ip

    def write_custom(self, message: str, request: Request):
        """Écrit un message personnalisé avec l'IP du client"""
        client_ip = self.get_client_ip(request)
        self.logger.info(f"{message} FROM {client_ip}")

    def write_debug(self, error: str):
        """Écrit un message de debug"""
        self.logger.debug(str(error))

    def write_info(
        self,
        request: Request,
        role: str | None = None,
        error: HTTPException | None = None,
    ):
        """
        Écrit un message d'information détaillé incluant:
        - Le rôle de l'utilisateur
        - Le code d'erreur HTTP et son détail si présent
        - La méthode HTTP et le chemin de la requête
        - L'IP du client
        """
        print("informing")
        client_ip = self.get_client_ip(request=request)
        self.logger.info(
            f"{role if role else ''} - {error.status_code if error else ''} - {error.detail if error else ''} - {request.method} - ON {request.url.path} FROM: {client_ip}"
        )

    def write_log(self, msg: str, request: Request):
        """Écrit un message d'avertissement avec l'IP du client"""
        client_ip = self.get_client_ip(request=request)
        self.logger.warning(f"{msg} FROM: {client_ip}")

    def write_valid(self, request: Request, exc: Exception):
        """Écrit un message d'avertissement pour une exception avec l'IP du client"""
        client_ip = self.get_client_ip(request=request)
        self.logger.warning(f"{exc} FROM: {client_ip}")

    def setup_logging(self):
        """Configure le système de logging avec:
        - Un logger nommé
        - Un format de log standardisé
        - Un handler pour la console
        - Un handler pour les fichiers avec rotation quotidienne
        """
        # Nom du logger
        logger_name = "CMV_PATIENTS"
        self.logger = logging.getLogger(logger_name)

        # Format des logs
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)

        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Handler pour les fichiers avec rotation
        log_file = "app/logs/fastapi-efk.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file, when="midnight", backupCount=5
        )
        file_handler.setFormatter(formatter)

        # Ajout des handlers et configuration du niveau de log
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)

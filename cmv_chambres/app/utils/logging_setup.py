# Import des modules nécessaires
import logging
import logging.handlers

from fastapi import Request, HTTPException


class LoggerSetup:
    """Classe singleton pour configurer et gérer les logs de l'application"""

    # Instance unique de la classe
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
        Récupère l'adresse IP du client à partir de l'objet Request.

        Args:
            request (Request): L'objet Request FastAPI

        Returns:
            str: L'adresse IP du client
        """
        client_ip = request.headers.get("X-Real-IP") or request.headers.get(
            "X-Forwarded-For"
        )
        return client_ip

    def write_custom(self, message: str, request: Request):
        """
        Écrit un message personnalisé dans les logs avec l'IP du client.

        Args:
            message (str): Le message à logger
            request (Request): L'objet Request FastAPI
        """
        client_ip = self.get_client_ip(request)
        self.logger.info(f"{message} FROM {client_ip}")

    def write_debug(self, error: str):
        """
        Écrit un message de debug dans les logs.

        Args:
            error (str): Le message d'erreur à logger
        """
        self.logger.debug(str(error))

    def write_info(
        self,
        request: Request,
        role: str | None = None,
        error: HTTPException | None = None,
    ):
        """
        Écrit un message d'information détaillé dans les logs.

        Args:
            request (Request): L'objet Request FastAPI
            role (str, optional): Le rôle de l'utilisateur
            error (HTTPException, optional): L'exception HTTP si présente
        """
        print("informing")
        client_ip = self.get_client_ip(request=request)
        self.logger.info(
            f"{role if role else ''} - {error.status_code if error else ''} - {error.detail if error else ''} - {request.method} - ON {request.url.path} FROM: {client_ip}"
        )

    def write_log(self, msg: str, request: Request):
        """
        Écrit un message d'avertissement dans les logs.

        Args:
            msg (str): Le message à logger
            request (Request): L'objet Request FastAPI
        """
        client_ip = self.get_client_ip(request=request)
        self.logger.warning(f"{msg} FROM: {client_ip}")

    def write_valid(self, request: Request, exc: Exception):
        """
        Écrit une exception de validation dans les logs.

        Args:
            request (Request): L'objet Request FastAPI
            exc (Exception): L'exception à logger
        """
        client_ip = self.get_client_ip(request=request)
        self.logger.warning(f"{exc} FROM: {client_ip}")

    def setup_logging(self):
        """Configure les handlers et le format des logs"""

        # Nom du logger
        logger_name = "AFFRANCHISSEMENT"
        self.logger = logging.getLogger(logger_name)

        # Format des logs
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)

        # Handler pour la console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Handler pour la rotation des fichiers de log
        log_file = "app/logs/fastapi-efk.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file, when="midnight", backupCount=5
        )
        file_handler.setFormatter(formatter)

        # Ajout des handlers au logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)

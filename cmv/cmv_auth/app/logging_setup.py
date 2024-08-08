import logging
import logging.handlers

from fastapi import Request


class LoggerSetup:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSetup, cls).__new__(cls)
            cls._instance.setup_logging()
        return cls._instance

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        Fonction utilitaire pour récupérer l'adresse IP du client à partir de l'objet Request.
        """
        client_ip = request.headers.get("X-Real-IP") or request.headers.get(
            "X-Forwarded-For"
        )
        return client_ip or request.client.host

    def write_log(self, msg: str, request: Request):
        client_ip = self.get_client_ip(request=request)
        self.logger.warning(f"{msg} FROM: {client_ip}")

    def setup_logging(self):
        # Logger name
        logger_name = "CMV"  # Change this to your desired logger name
        self.logger = logging.getLogger(logger_name)

        # Log format
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # TimeRotatingFileHandler
        log_file = "app/logs/fastapi-efk.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file, when="midnight", backupCount=5
        )
        file_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

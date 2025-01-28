import logging
import logging.handlers

from fastapi import Request, HTTPException


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
        return client_ip

    def write_custom(self, message: str, request: Request):
        client_ip = self.get_client_ip(request)
        self.logger.info(f"{message} FROM {client_ip}")

    def write_debug(self, error: str):
        self.logger.debug(str(error))

    def write_info(
        self,
        request: Request,
        role: str | None = None,
        error: HTTPException | None = None,
    ):
        print("informing")
        client_ip = self.get_client_ip(request=request)
        self.logger.info(
            f"{role if role else ''} - {error.status_code if error else ''} - {error.detail if error else ''} - {request.method} - ON {request.url.path} FROM: {client_ip}"
        )

    def write_log(self, msg: str, request: Request):
        client_ip = self.get_client_ip(request=request)
        self.logger.warning(f"{msg} FROM: {client_ip}")

    def write_valid(self, request: Request, exc: Exception):
        client_ip = self.get_client_ip(request=request)
        self.logger.warning(f"{exc} FROM: {client_ip}")

    def setup_logging(self):
        # Logger name
        logger_name = "CMV_PATIENTS"  # Change this to your desired logger name
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
        self.logger.setLevel(logging.DEBUG)

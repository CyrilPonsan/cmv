from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        csp_options: Dict = None,
        hsts_options: Dict = None,
        xfo_options: Dict = None,
    ):
        super().__init__(app)
        self.csp_options = csp_options or {}
        self.hsts_options = hsts_options or {}
        self.xfo_options = xfo_options or {}

    def get_csp_header(self) -> str:
        """Génère l'en-tête Content Security Policy"""
        default_csp = {
            "default-src": ["'self'"],
            "base-uri": ["'self'"],
            "block-all-mixed-content": [],
            "font-src": ["'self'", "https:", "data:"],
            "frame-ancestors": ["'self'"],
            "img-src": ["'self'", "data:", "https:"],
            "object-src": ["'none'"],
            "script-src": ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
            "script-src-attr": ["'none'"],
            "style-src": ["'self'", "'unsafe-inline'"],
            "upgrade-insecure-requests": [],
        }

        # Fusionner avec les options personnalisées
        csp = {**default_csp, **self.csp_options}

        # Construire la chaîne CSP
        policy_parts = []
        for key, value in csp.items():
            if value:
                policy_parts.append(f"{key} {' '.join(value)}")
            else:
                policy_parts.append(key)

        return "; ".join(policy_parts)

    def get_hsts_header(self) -> str:
        """Génère l'en-tête Strict-Transport-Security"""
        default_hsts = {"max-age": 31536000, "includeSubDomains": True, "preload": True}

        hsts = {**default_hsts, **self.hsts_options}
        parts = [f"max-age={hsts['max-age']}"]

        if hsts.get("includeSubDomains"):
            parts.append("includeSubDomains")
        if hsts.get("preload"):
            parts.append("preload")

        return "; ".join(parts)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Supprimer les en-têtes sensibles
        sensitive_headers = ["X-Powered-By", "Server"]
        for header in sensitive_headers:
            if header in response.headers:
                del response.headers[header]

        # Définir les en-têtes de sécurité
        security_headers = {
            # Protection XSS
            "X-XSS-Protection": "1; mode=block",
            # Protection contre le sniffing de type MIME
            "X-Content-Type-Options": "nosniff",
            # Protection contre le clickjacking
            "X-Frame-Options": "SAMEORIGIN",
            # Contrôle du référent HTTP
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Politique de permissions
            "Permissions-Policy": (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            ),
            # Protection contre le préchargement DNS
            "X-DNS-Prefetch-Control": "off",
            # Politique de téléchargement pour IE
            "X-Download-Options": "noopen",
            # Politique de domaine croisé
            "X-Permitted-Cross-Domain-Policies": "none",
            # HSTS (HTTP Strict Transport Security)
            "Strict-Transport-Security": self.get_hsts_header(),
            # Content Security Policy
            "Content-Security-Policy": self.get_csp_header(),
        }

        # Ajouter les en-têtes à la réponse
        for header_key, header_value in security_headers.items():
            response.headers[header_key] = header_value

        return response

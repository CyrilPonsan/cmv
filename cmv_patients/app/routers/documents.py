from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.dependancies.auth import check_authorization
from app.dependancies.db_session import get_db
from app.schemas.user import InternalPayload
from app.services.documents import get_documents_service
from app.utils.logging_setup import LoggerSetup

router = APIRouter(prefix="/documents", tags=["documents"])
logger = LoggerSetup()

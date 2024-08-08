from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.dependancies.db_session import get_db
from app.routers import api
from app.sql import models
from app.sql.database import engine
from app.dependancies.rate_limiter import custom_callback, service_name_identifier
from .services.fixtures import create_fixtures
from .logging_setup import LoggerSetup

REDIS_URL = "redis://redis:6379"

# setup root logger
logger_setup = LoggerSetup()

# get logger for module
LOGGER = logger_setup.logger

models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url(REDIS_URL, encoding="utf8")
    await FastAPILimiter.init(
        redis=redis_connection,
        identifier=service_name_identifier,
        http_callback=custom_callback,
    )
    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)


app.include_router(api.router)
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" @app.on_event("startup")
async def startup():
    LOGGER.info("--- Start up App ---")

@app.on_event("shutdown")
async def shutdown():
    LOGGER.info("--- shutdown App ---") """


@app.get("/fixtures")
def fixtures(db: Session = Depends(get_db)):
    print("fixturing all night long")
    return create_fixtures(db)


# Serve the Vue app in production mode
try:
    # Directory where Vue app build output is located
    build_dir = Path(__file__).resolve().parent / "dist"
    index_path = build_dir / "index.html"

    print(f"build dir : {build_dir}")
    print(f"index {index_path}")

    # Serve assets files from the build directory
    app.mount("/assets", StaticFiles(directory=build_dir / "assets"), name="assets")

    # Catch-all route for SPA
    @app.get("/{catchall:path}")
    async def serve_spa(catchall: str):
        # If the requested file exists, serve it, else serve index.html
        path = build_dir / catchall
        if path.is_file():
            return FileResponse(path)
        return FileResponse(index_path)

except RuntimeError:
    # The build directory does not exist
    print("No build directory found. Running in development mode.")

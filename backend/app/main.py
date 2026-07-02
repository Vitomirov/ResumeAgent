from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import export, health, inputs, preview, tailor
from app.core.config import settings
from app.core.errors import AppError, NotFoundError, ValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ResumeAgent API",
        description="Local AI Resume Tailoring Agent",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(ValidationError)
    async def validation_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message, "code": exc.code})

    app.include_router(health.router)
    app.include_router(inputs.router, prefix="/inputs", tags=["inputs"])
    app.include_router(tailor.router, prefix="/tailor", tags=["tailor"])
    app.include_router(preview.router, prefix="/preview", tags=["preview"])
    app.include_router(export.router, prefix="/export", tags=["export"])

    return app


app = create_app()

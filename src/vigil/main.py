from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from vigil_tasks.analysis import run_inference

from vigil.core.config import settings
from vigil.core.minio.client import upload_file

from vigil.modules.auth.presentation.api.v1.router import router as auth_router
from vigil.modules.auth.presentation.exception_handlers import register_exception_handlers as register_auth_handlers

from vigil.modules.users.presentation.api.v1.router import router as users_router

def create_app() -> FastAPI:
    application = FastAPI(
        title="Vigil System",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_auth_handlers(application)

    @application.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/test-task")
    async def test_task():
        run_inference.delay("test-123") # type: ignore
        return {"status": "dispatched"}

    @application.get("/test-upload")
    async def test_upload():
        upload_file()
        return {"status": "uploaded"}
    
    application.include_router(auth_router)
    application.include_router(users_router)

    return application


app = create_app()

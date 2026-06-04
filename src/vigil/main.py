from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vigil.core.config import settings

from vigil.shared.exception_handlers import register_exception_handlers

from vigil.modules.auth.presentation.api.v1.router import router as auth_router
from vigil.modules.auth.presentation.exception_handlers import register_exception_handlers as register_auth_handlers

from vigil.modules.users.presentation.api.v1.router import router as users_router
from vigil.modules.users.presentation.exception_handlers import register_exception_handler as register_users_handlers

from vigil.modules.videos.presentation.api.v1.router import router as videos_router
from vigil.modules.videos.presentation.exception_handlers import register_exception_handlers as register_videos_handlers

from vigil.modules.analysis.presentation.api.v1.router import router as analyses_router
from vigil.modules.analysis.presentation.exception_handlers import register_exception_handlers as register_analyses_handlers

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

    register_exception_handlers(application)
    register_auth_handlers(application)
    register_users_handlers(application)
    register_videos_handlers(application)
    register_analyses_handlers(application)

    if settings.debug:
        @application.get("/health")
        async def health_check() -> dict[str, str]:
            return {"status": "ok"}
    
    application.include_router(auth_router)
    application.include_router(users_router)
    application.include_router(videos_router)
    application.include_router(analyses_router)

    return application


app = create_app()

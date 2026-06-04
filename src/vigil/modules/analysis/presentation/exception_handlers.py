from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..application.exceptions import AnalysisAccessDeniedError
from ..domain.exceptions import AnalysisNotFoundError


def register_exception_handlers(app: FastAPI) -> None:

    # --- access denied ---

    @app.exception_handler(AnalysisAccessDeniedError)
    async def analysis_access_denied_handler(request: Request, exc: AnalysisAccessDeniedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Analysis access denied"}
        )
    
    @app.exception_handler(AnalysisNotFoundError)
    async def analysis_not_found_handler(request: Request, exc: AnalysisNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Analysis not found"}
        )
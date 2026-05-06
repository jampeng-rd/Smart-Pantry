"""API 錯誤處理。"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_error_handlers(app: FastAPI) -> None:
    """註冊統一錯誤回應格式。"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        """處理 HTTP 例外。"""
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "data": None, "message": str(exc.detail)},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        """處理請求驗證例外。"""
        return JSONResponse(
            status_code=422,
            content={"status": "error", "data": None, "message": str(exc.errors())},
        )

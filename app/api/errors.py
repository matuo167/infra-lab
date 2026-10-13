from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def validation_error_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        return JSONResponse(status_code=500, content={"error": {"code": "internal_error"}})
    details: list[dict[str, Any]] = []
    for error in exc.errors():
        details.append(
            {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
        )
    return JSONResponse(
        status_code=422, content={"error": {"code": "validation_error", "details": details}}
    )

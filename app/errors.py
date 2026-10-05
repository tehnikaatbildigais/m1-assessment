"""Kļūdu atbildes pēc līguma (API contract) vienotās kļūdu shēmas."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("ezermala.errors")


class SubmissionNotFound(Exception):
    pass


class InvalidState(Exception):
    pass


def _field(error: dict) -> str:
    # loc piemērs: ("body", "personalCode"). Pirmais elements ir vieta pieprasījumā.
    if error["type"] == "json_invalid":
        return "request"
    rest = [str(part) for part in error["loc"][1:]]
    return ".".join(rest) if rest else "request"


def _issue(error: dict) -> str:
    if error["type"] == "missing":
        return "REQUIRED"
    if error["type"] == "string_too_long":
        return "TOO_LONG"
    return "INVALID_FORMAT"


def error_response(status: int, code: str, message: str, details=None) -> JSONResponse:
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Ievadīto vērtību atbildē neatkārtojam: tajā var būt personas dati.
        details = [{"field": _field(e), "issue": _issue(e)} for e in exc.errors()]
        return error_response(
            400, "VALIDATION_ERROR", "Request validation failed", details
        )

    @app.exception_handler(SubmissionNotFound)
    async def not_found(request: Request, exc: SubmissionNotFound):
        return error_response(404, "NOT_FOUND", "Submission not found")

    @app.exception_handler(InvalidState)
    async def invalid_state(request: Request, exc: InvalidState):
        return error_response(
            409, "INVALID_STATE", "Action not allowed in the current status"
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        # Kļūdas tekstu neatgriežam un nežurnalējam: tajā var būt iekšēja
        # informācija vai personas dati. Pietiek ar kļūdas tipu.
        logger.error(
            "Neparedzēta kļūda: %s %s (%s)",
            request.method,
            request.url.path,
            type(exc).__name__,
        )
        return error_response(500, "INTERNAL_ERROR", "Internal server error")

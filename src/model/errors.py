from enum import StrEnum

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorCode(StrEnum):
    database_connection_error = "database_connection_error"
    unknown_error = "unknown_error"
    invalid_request = "invalid_request"
    not_found = "not_found"


class ErrorResponse(BaseModel):
    code: ErrorCode
    message: str = ""


class ServiceError(Exception):
    def __init__(
        self, code: ErrorCode, message: str = "", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ) -> None:
        self.error_response = ErrorResponse(code=code, message=message)
        self.status_code = status_code
        super().__init__(message)

    def to_json_response(self, status_code: int | None = None) -> JSONResponse:
        return JSONResponse(status_code=status_code or self.status_code, content=self.error_response.model_dump())

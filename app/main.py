from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DuplicateGooglePlaceIdError,
    ExternalApiError,
    RestaurantNotFoundError,
)
from app.routers import places, restaurants

app = FastAPI(title="My Food Map Backend", version="0.1.0")

app.include_router(restaurants.router)
app.include_router(places.router)


def _error_response(code: str, message: str, status_code: int, details: dict | None = None):
    # Design Ref: §6.2 — Error Response Format
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details or {}}},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return _error_response("INVALID_INPUT", "Invalid input", 400, {"errors": exc.errors()})


@app.exception_handler(RestaurantNotFoundError)
async def restaurant_not_found_handler(request: Request, exc: RestaurantNotFoundError):
    return _error_response("NOT_FOUND", str(exc), 404)


@app.exception_handler(DuplicateGooglePlaceIdError)
async def duplicate_google_place_id_handler(request: Request, exc: DuplicateGooglePlaceIdError):
    return _error_response("CONFLICT", str(exc), 409)


@app.exception_handler(ExternalApiError)
async def external_api_error_handler(request: Request, exc: ExternalApiError):
    return _error_response("EXTERNAL_API_ERROR", str(exc), 502)

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalApiError

# Design Ref: §7.4 (v0.2) — no retry, 5s timeout
_TIMEOUT_SECONDS = 5.0
_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
_FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.location"


class GooglePlacesClient:
    def search_places(self, query: str) -> list[dict]:
        try:
            response = httpx.post(
                _SEARCH_URL,
                json={"textQuery": query},
                headers={
                    "X-Goog-Api-Key": settings.google_places_api_key,
                    "X-Goog-FieldMask": _FIELD_MASK,
                },
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalApiError(str(exc)) from exc

        return response.json().get("places", [])

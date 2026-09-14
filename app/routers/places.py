from fastapi import APIRouter, Query

from app.clients.google_places_client import GooglePlacesClient
from app.schemas.place import PlaceCandidate
from app.services.google_places_service import GooglePlacesService

router = APIRouter(prefix="/places", tags=["places"])


@router.get("/search")
def search_places(query: str = Query(..., min_length=1)) -> dict[str, list[PlaceCandidate]]:
    # Design Ref: §4.2 GET /places/search
    service = GooglePlacesService(GooglePlacesClient())
    candidates = service.search(query)
    return {"data": candidates}

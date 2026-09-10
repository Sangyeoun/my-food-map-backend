from app.clients.google_places_client import GooglePlacesClient
from app.schemas.place import PlaceCandidate


class GooglePlacesService:
    # Design Ref: §2.3 — Client 호출을 위임받아 도메인 스키마로 변환
    def __init__(self, client: GooglePlacesClient):
        self.client = client

    def search(self, query: str) -> list[PlaceCandidate]:
        raw_places = self.client.search_places(query)
        return [self._to_candidate(place) for place in raw_places]

    @staticmethod
    def _to_candidate(place: dict) -> PlaceCandidate:
        location = place.get("location", {})
        return PlaceCandidate(
            google_place_id=place["id"],
            name=place.get("displayName", {}).get("text", ""),
            address=place.get("formattedAddress", ""),
            latitude=location.get("latitude", 0.0),
            longitude=location.get("longitude", 0.0),
        )

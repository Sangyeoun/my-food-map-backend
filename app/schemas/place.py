from pydantic import BaseModel


class PlaceCandidate(BaseModel):
    # Design Ref: §4.2 GET /places/search response item
    google_place_id: str
    name: str
    address: str
    latitude: float
    longitude: float

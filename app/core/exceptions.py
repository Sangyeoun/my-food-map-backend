class RestaurantNotFoundError(Exception):
    # Design Ref: §6.1 — 404 Restaurant not found
    pass


class DuplicateGooglePlaceIdError(Exception):
    # Design Ref: §6.1 — 409 Duplicate google_place_id
    pass


class ExternalApiError(Exception):
    # Design Ref: §6.1 — 502 Google Places API error
    pass

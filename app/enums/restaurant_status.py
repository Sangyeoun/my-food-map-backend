import enum


class RestaurantStatus(str, enum.Enum):
    VISITED = "VISITED"
    WANT_TO_GO = "WANT_TO_GO"

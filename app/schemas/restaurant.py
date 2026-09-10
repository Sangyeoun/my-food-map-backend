from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums.restaurant_status import RestaurantStatus


class RestaurantCreate(BaseModel):
    # Design Ref: §4.2 POST /restaurants
    google_place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    status: RestaurantStatus
    my_rating: int | None = Field(default=None, ge=1, le=5)
    memo: str | None = None
    tags: list[str] = Field(default_factory=list)


class RestaurantUpdate(BaseModel):
    # Design Ref: §4.2 PATCH /restaurants/{id} — 모든 필드 optional, 제공된 필드만 수정
    # tags가 요청 body에 포함되면 전체 교체(replace) 정책 적용 (Design v0.2)
    status: RestaurantStatus | None = None
    my_rating: int | None = Field(default=None, ge=1, le=5)
    memo: str | None = None
    tags: list[str] | None = None


class RestaurantResponse(BaseModel):
    id: int
    google_place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    status: RestaurantStatus
    my_rating: int | None
    memo: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

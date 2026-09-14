from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.enums.restaurant_status import RestaurantStatus
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


def get_restaurant_service(db: Session = Depends(get_db)) -> RestaurantService:
    return RestaurantService(RestaurantRepository(db), TagRepository(db))


def _to_response(restaurant) -> RestaurantResponse:
    return RestaurantResponse(
        id=restaurant.id,
        google_place_id=restaurant.google_place_id,
        name=restaurant.name,
        address=restaurant.address,
        latitude=restaurant.latitude,
        longitude=restaurant.longitude,
        status=restaurant.status,
        my_rating=restaurant.my_rating,
        memo=restaurant.memo,
        tags=[tag.name for tag in restaurant.tags],
        created_at=restaurant.created_at,
        updated_at=restaurant.updated_at,
    )


@router.get("")
def list_restaurants(
    status_filter: RestaurantStatus | None = None,
    service: RestaurantService = Depends(get_restaurant_service),
) -> dict[str, list[RestaurantResponse]]:
    # Design Ref: §4.2 GET /restaurants?status=
    restaurants = service.list_restaurants(status=status_filter)
    return {"data": [_to_response(r) for r in restaurants]}


@router.get("/{restaurant_id}")
def get_restaurant(
    restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)
) -> dict[str, RestaurantResponse]:
    restaurant = service.get_restaurant(restaurant_id)
    return {"data": _to_response(restaurant)}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_restaurant(
    data: RestaurantCreate, service: RestaurantService = Depends(get_restaurant_service)
) -> dict[str, RestaurantResponse]:
    # Plan SC: Restaurant CRUD API 5개 엔드포인트 모두 구현
    restaurant = service.create_restaurant(data)
    return {"data": _to_response(restaurant)}


@router.patch("/{restaurant_id}")
def update_restaurant(
    restaurant_id: int,
    data: RestaurantUpdate,
    service: RestaurantService = Depends(get_restaurant_service),
) -> dict[str, RestaurantResponse]:
    restaurant = service.update_restaurant(restaurant_id, data)
    return {"data": _to_response(restaurant)}


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)
) -> None:
    # Design Ref: §3.3 — Hard delete + CASCADE (FR-05)
    service.delete_restaurant(restaurant_id)

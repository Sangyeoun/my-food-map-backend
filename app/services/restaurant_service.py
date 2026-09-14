from app.core.exceptions import DuplicateGooglePlaceIdError, RestaurantNotFoundError
from app.models.restaurant import Restaurant
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate


class RestaurantService:
    # Design Ref: §2.0 Option C — Tag 처리를 restaurant_service에서 함께 담당
    def __init__(self, restaurant_repo: RestaurantRepository, tag_repo: TagRepository):
        self.restaurant_repo = restaurant_repo
        self.tag_repo = tag_repo

    def list_restaurants(self, status=None) -> list[Restaurant]:
        return self.restaurant_repo.list(status=status)

    def get_restaurant(self, restaurant_id: int) -> Restaurant:
        restaurant = self.restaurant_repo.get_by_id(restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError(f"Restaurant {restaurant_id} not found")
        return restaurant

    def create_restaurant(self, data: RestaurantCreate) -> Restaurant:
        # Design Ref: §4.2 POST /restaurants — 409 on duplicate google_place_id
        if self.restaurant_repo.get_by_google_place_id(data.google_place_id) is not None:
            raise DuplicateGooglePlaceIdError(
                f"google_place_id {data.google_place_id} already exists"
            )
        tags = self.tag_repo.get_or_create_many(data.tags)
        restaurant = Restaurant(
            google_place_id=data.google_place_id,
            name=data.name,
            address=data.address,
            latitude=data.latitude,
            longitude=data.longitude,
            status=data.status,
            my_rating=data.my_rating,
            memo=data.memo,
            tags=tags,
        )
        return self.restaurant_repo.create(restaurant)

    def update_restaurant(self, restaurant_id: int, data: RestaurantUpdate) -> Restaurant:
        # Design Ref: §4.2 PATCH — tags 포함 시 전체 교체(replace), 미포함 시 기존 유지 (Design v0.2)
        restaurant = self.get_restaurant(restaurant_id)
        updates = data.model_dump(exclude_unset=True, exclude={"tags"})
        for field, value in updates.items():
            setattr(restaurant, field, value)
        if data.tags is not None:
            restaurant.tags = self.tag_repo.get_or_create_many(data.tags)
        return self.restaurant_repo.create(restaurant)

    def delete_restaurant(self, restaurant_id: int) -> None:
        restaurant = self.get_restaurant(restaurant_id)
        self.restaurant_repo.delete(restaurant)

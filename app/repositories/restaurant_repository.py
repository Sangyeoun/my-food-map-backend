from sqlalchemy.orm import Session

from app.enums.restaurant_status import RestaurantStatus
from app.models.restaurant import Restaurant


class RestaurantRepository:
    # Design Ref: §9.1 — Repository는 순수 CRUD 쿼리만 담당
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, restaurant_id: int) -> Restaurant | None:
        return self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    def get_by_google_place_id(self, google_place_id: str) -> Restaurant | None:
        return (
            self.db.query(Restaurant)
            .filter(Restaurant.google_place_id == google_place_id)
            .first()
        )

    def list(self, status: RestaurantStatus | None = None) -> list[Restaurant]:
        # Design Ref: §4.2 GET /restaurants?status=
        query = self.db.query(Restaurant)
        if status is not None:
            query = query.filter(Restaurant.status == status)
        return query.all()

    def create(self, restaurant: Restaurant) -> Restaurant:
        self.db.add(restaurant)
        self.db.flush()
        self.db.refresh(restaurant)
        return restaurant

    def delete(self, restaurant: Restaurant) -> None:
        # Design Ref: §3.3 — ON DELETE CASCADE로 restaurant_tags 자동 정리 (FR-05)
        self.db.delete(restaurant)
        self.db.flush()

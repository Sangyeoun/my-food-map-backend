from sqlalchemy.orm import Session

from app.models.tag import Tag


class TagRepository:
    # Design Ref: §2.3 — restaurant_service가 위임하는 Tag CRUD 전담
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Tag | None:
        return self.db.query(Tag).filter(Tag.name == name).first()

    def get_or_create(self, name: str) -> Tag:
        # Design Ref: FR-07 — 존재하면 재사용, 없으면 생성
        tag = self.get_by_name(name)
        if tag is not None:
            return tag
        tag = Tag(name=name)
        self.db.add(tag)
        self.db.flush()
        return tag

    def get_or_create_many(self, names: list[str]) -> list[Tag]:
        return [self.get_or_create(name) for name in names]

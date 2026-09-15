# Design Ref: §8.2 L1 API Test Scenarios #1-10
from sqlalchemy import text

from tests.conftest import engine

RESTAURANT_PAYLOAD = {
    "google_place_id": "ChIJ1",
    "name": "이치란 라멘",
    "address": "도쿄도 시부야구",
    "latitude": 35.6595,
    "longitude": 139.7005,
    "status": "WANT_TO_GO",
    "tags": ["라멘", "일본"],
}


def _create_restaurant(client, **overrides):
    payload = {**RESTAURANT_PAYLOAD, **overrides}
    response = client.post("/restaurants", json=payload)
    assert response.status_code == 201
    return response.json()["data"]


def test_list_restaurants_returns_array(client):
    # Scenario #1: 전체 목록 조회
    _create_restaurant(client)

    response = client.get("/restaurants")

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_list_restaurants_filters_by_status(client):
    # Scenario #2: status 필터 적용
    _create_restaurant(client, google_place_id="ChIJ-visited", status="VISITED")
    _create_restaurant(client, google_place_id="ChIJ-want", status="WANT_TO_GO")

    response = client.get("/restaurants?status=VISITED")

    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) == 1
    assert all(item["status"] == "VISITED" for item in results)


def test_list_restaurants_filters_by_want_to_go_status(client):
    # Scenario #2b: status=WANT_TO_GO 필터 적용
    _create_restaurant(client, google_place_id="ChIJ-visited-2", status="VISITED")
    _create_restaurant(client, google_place_id="ChIJ-want-2", status="WANT_TO_GO")

    response = client.get("/restaurants?status=WANT_TO_GO")

    assert response.status_code == 200
    results = response.json()["data"]
    assert len(results) == 1
    assert all(item["status"] == "WANT_TO_GO" for item in results)


def test_list_restaurants_without_status_returns_all(client):
    # Scenario #2c: status 파라미터 없이 호출 시 전체 반환
    _create_restaurant(client, google_place_id="ChIJ-visited-3", status="VISITED")
    _create_restaurant(client, google_place_id="ChIJ-want-3", status="WANT_TO_GO")

    response = client.get("/restaurants")

    assert response.status_code == 200
    results = response.json()["data"]
    statuses = {item["status"] for item in results}
    assert "VISITED" in statuses
    assert "WANT_TO_GO" in statuses


def test_get_restaurant_by_existing_id(client):
    # Scenario #3: 존재하는 id 단건 조회
    created = _create_restaurant(client)

    response = client.get(f"/restaurants/{created['id']}")

    assert response.status_code == 200
    assert response.json()["data"]["id"] == created["id"]


def test_get_restaurant_by_nonexistent_id_returns_404(client):
    # Scenario #4: 존재하지 않는 id 조회
    response = client.get("/restaurants/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_create_restaurant_with_valid_data(client):
    # Scenario #5: 유효한 데이터로 생성
    response = client.post("/restaurants", json=RESTAURANT_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["data"]["id"] is not None

    listed = client.get("/restaurants").json()["data"]
    assert any(r["google_place_id"] == RESTAURANT_PAYLOAD["google_place_id"] for r in listed)


def test_create_restaurant_missing_required_field_returns_400(client):
    # Scenario #6: 필수 필드 누락
    response = client.post("/restaurants", json={"name": "필드 누락"})

    assert response.status_code == 400
    assert "errors" in response.json()["error"]["details"]


def test_create_restaurant_duplicate_google_place_id_returns_409(client):
    # Scenario #7: 중복 google_place_id
    _create_restaurant(client)

    response = client.post("/restaurants", json=RESTAURANT_PAYLOAD)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_create_restaurant_with_visited_date(client):
    # visited_date 저장 및 응답 확인
    created = _create_restaurant(
        client, status="VISITED", visited_date="2026-09-10"
    )

    assert created["visited_date"] == "2026-09-10"


def test_create_restaurant_without_visited_date_defaults_to_null(client):
    # visited_date 미제공 시 null
    created = _create_restaurant(client)

    assert created["visited_date"] is None


def test_patch_restaurant_updates_visited_date(client):
    # PATCH로 visited_date만 수정, 나머지 필드 유지
    created = _create_restaurant(client)

    response = client.patch(
        f"/restaurants/{created['id']}",
        json={"status": "VISITED", "visited_date": "2026-09-12"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["visited_date"] == "2026-09-12"
    assert data["status"] == "VISITED"


def test_patch_restaurant_updates_only_provided_fields(client):
    # Scenario #8: status/my_rating/memo 부분 수정, 나머지 유지
    created = _create_restaurant(client)

    response = client.patch(
        f"/restaurants/{created['id']}",
        json={"status": "VISITED", "my_rating": 4, "memo": "재방문 의사 있음"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "VISITED"
    assert data["my_rating"] == 4
    assert data["memo"] == "재방문 의사 있음"
    assert data["name"] == RESTAURANT_PAYLOAD["name"]
    assert data["tags"] == RESTAURANT_PAYLOAD["tags"]


def test_delete_existing_restaurant(client):
    # Scenario #9: 존재하는 id 삭제, 이후 조회 404, restaurant_tags에도 row 없음
    created = _create_restaurant(client)

    response = client.delete(f"/restaurants/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/restaurants/{created['id']}").status_code == 404

    with engine.connect() as conn:
        orphan_count = conn.execute(
            text("SELECT COUNT(*) FROM restaurant_tags WHERE restaurant_id = :rid"),
            {"rid": created["id"]},
        ).scalar()
    assert orphan_count == 0


def test_delete_nonexistent_restaurant_returns_404(client):
    # Scenario #10: 존재하지 않는 id 삭제
    response = client.delete("/restaurants/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"

# My Food Map - Backend

한국과 일본을 중심으로, 방문했던 맛집과 앞으로 방문하고 싶은 가게를 지도 위에 기록하고 관리하는 개인 맛집 지도 서비스의 Backend Repository.

> Google Maps의 장소 데이터 + 나만의 방문 기록

을 결합한 개인 맛집 데이터베이스를 만드는 것이 목적이다.

관련 Repository:

```text
my-food-map-frontend    UI / Map / User Interaction
my-food-map-backend      API / Business Logic / Database   (본 저장소)
my-food-map-infrastructure   AWS / Deployment / Infrastructure
```

---

## 1. Responsibility

이 Repository는 다음을 담당한다.

```text
Restaurant CRUD

Visit 관리

Tag 관리

Favorite 관리

개인 데이터 관리

Google Places 연계

Business Logic
```

Google Maps Platform이 제공하는 장소 데이터(Place ID, 이름, 주소, 좌표 등)와,
서비스가 직접 관리하는 개인 데이터(VISITED/WANT_TO_GO, 평점, 메모, 태그, 방문 기록 등)를
분리하여 다룬다.

```text
Google Place
     +
Personal Data
     =
My Restaurant
```

---

## 2. Tech Stack

```text
Python
FastAPI
SQLAlchemy
Pydantic
PostgreSQL
```

향후 위치 기반 기능이 필요해지면 PostgreSQL + PostGIS로 확장한다.

---

## 3. Architecture

Layer 구조:

```text
Router
  ↓
Service
  ↓
Repository
  ↓
Database
```

외부 API(Google Places)를 사용하는 경우:

```text
Router
  ↓
Service
  ├── Repository → PostgreSQL
  └── Client     → Google API
```

각 Layer의 책임:

- **Router**: HTTP Request/Response, Validation, Status Code
- **Service**: Business Logic, VISITED/WANT_TO_GO 처리, Google 데이터와 Personal 데이터 조합
- **Repository**: Database CRUD, SQLAlchemy Query
- **Client**: 외부 API 통신 (Google Places API)

---

## 4. Project Structure

```text
my-food-map-backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── routers/
│   │   ├── restaurants.py
│   │   ├── visits.py
│   │   └── tags.py
│   │
│   ├── schemas/
│   │   ├── restaurant.py
│   │   ├── visit.py
│   │   └── tag.py
│   │
│   ├── models/
│   │   ├── restaurant.py
│   │   ├── visit.py
│   │   └── tag.py
│   │
│   ├── repositories/
│   │   ├── restaurant_repository.py
│   │   ├── visit_repository.py
│   │   └── tag_repository.py
│   │
│   ├── services/
│   │   ├── restaurant_service.py
│   │   └── google_places_service.py
│   │
│   ├── clients/
│   │   └── google_places_client.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   └── enums/
│       └── restaurant_status.py
│
├── tests/
│
├── migrations/
│
├── pyproject.toml
│
└── Dockerfile
```

---

## 5. Database Design (Phase 1)

### restaurants

```text
id
google_place_id

name
address

latitude
longitude

status        (VISITED | WANT_TO_GO)

my_rating
memo

created_at
updated_at
```

### tags

```text
id
name
```

### restaurant_tags

```text
restaurant_id
tag_id
```

관계: `Restaurant N:M Tag`

### Phase 2 확장 - restaurant_visits

방문 기록은 Restaurant에 직접 넣지 않고 별도 Entity로 관리한다.

```text
id
restaurant_id
visited_at
rating
memo
created_at
```

관계: `Restaurant 1:N RestaurantVisit`

---

## 6. API Design (Phase 1)

### Restaurant

```http
GET    /restaurants
GET    /restaurants/{restaurant_id}
POST   /restaurants
PATCH  /restaurants/{restaurant_id}
DELETE /restaurants/{restaurant_id}
```

### Filter

```http
GET /restaurants?status=VISITED
GET /restaurants?status=WANT_TO_GO
```

향후:

```http
GET /restaurants?tag=ramen
GET /restaurants?rating_gte=4
```

### Map

초기에는 `GET /restaurants` 결과 전체를 지도에 표시한다.
데이터가 많아지면 지도 영역 기반 API로 변경한다.

```http
GET /restaurants/map?north=35.8&south=35.6&east=139.9&west=139.6
```

향후 PostGIS 적용 시 공간 검색을 Backend에서 처리한다.

---

## 7. Development Phases

```text
Phase 1  MVP - Google Places 검색, 저장, VISITED/WANT_TO_GO, 평점/메모/태그, 지도 Marker
Phase 2  Personal Restaurant Database - 방문 기록, 즐겨찾기, 가격대, 카테고리, List View
Phase 3  Location Based Features - 현재 위치 기반 검색, 영역 조회, Marker Cluster
Phase 4  Analytics & Recommendation - 방문 통계, 추천, Heatmap
Phase 5  Optional Expansion - 로그인, 멀티 사용자, 공유, 사진 업로드
```

현재 우선 구현 대상은 **Phase 1**이며, Backend 관점의 완료 기준은 다음과 같다.

```text
1. Restaurant CRUD API 구현
2. Google Places 연계 (검색)
3. VISITED / WANT_TO_GO 상태 관리
4. 개인 평점 / 메모 / 태그 저장
5. Frontend와 연결되어 정상 동작
```

---

## 8. Local Development

Phase 1 기준 로컬 개발 환경:

```text
Backend      localhost:8000
PostgreSQL   Docker
```

(개발 환경 구성은 프로젝트 진행에 따라 본 섹션에 추가 예정)

---

## 9. Development Principle

```text
Keep It Simple
```

처음부터 Production 수준의 복잡한 Architecture를 만들지 않는다. MVP로 시작해 실제 사용하며
불편한 점을 확인하고 필요한 만큼 기능과 구조를 확장한다.

이 프로젝트의 목적 중 하나는 Frontend 학습이므로, Backend는 필요 이상으로 복잡하게 만들지 않고
Frontend 개발 속도를 뒷받침하는 수준으로 단순하게 유지한다.

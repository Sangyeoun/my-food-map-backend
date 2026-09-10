---
template: design
version: 1.3
description: PDCA Design phase document — FastAPI/PostgreSQL Backend (no BaaS)
variables:
  - feature: restaurant-mvp
  - date: 2026-09-08
  - author: SY LEE
  - project: my-food-map-backend
  - version: 0.1.0
---

# restaurant-mvp Design Document

> **Summary**: Google Places 검색 연계와 개인 방문 데이터(VISITED/WANT_TO_GO, 평점, 메모, 태그)를 결합한 Restaurant CRUD API의 FastAPI/PostgreSQL 기반 상세 설계.
>
> **Project**: my-food-map-backend
> **Version**: 0.1.0
> **Author**: SY LEE
> **Date**: 2026-09-08
> **Status**: Draft
> **Planning Doc**: [restaurant-mvp.plan.md](../../01-plan/features/restaurant-mvp.plan.md)

---

## Executive Summary

| Perspective | Content |
|-------------|---------|
| **Problem** | Restaurant CRUD + Google Places 연계를 어떤 계층 구조와 스키마로 구현할지 구체적 설계가 없다 |
| **Solution** | README 4-Layer(Router→Service→Repository→Database) 구조를 채택하고(Option C), Google Places는 Client로 분리, Tag는 restaurant_service에서 함께 처리 |
| **Function/UX Effect** | Frontend가 명확한 API 계약(§4)과 에러 포맷(§6)을 기준으로 연동 가능해짐 |
| **Core Value** | 과설계 없이 Phase 1 범위에 맞는 실용적 아키텍처로 빠른 구현과 유지보수성을 동시에 확보 |

---

## Context Anchor

> Copied from Plan document. Ensures strategic context survives Design→Do handoff.

| Key | Value |
|-----|-------|
| **WHY** | 개인이 방문/관심 맛집을 지도 기반으로 기록하고 개인 데이터(평점, 메모, 태그)를 관리할 수단이 없음 |
| **WHO** | 서비스 소유자 본인 (단일 사용자, 인증 없음) |
| **RISK** | Google Places API 매 검색 직접 호출로 인한 API 비용 증가 및 응답 지연 |
| **SUCCESS** | Restaurant CRUD API 동작 + Google Places 검색 연계 + VISITED/WANT_TO_GO 상태 관리 + Frontend 연동 정상 동작 |
| **SCOPE** | Phase 1(MVP)만 포함, Phase 2(방문 기록/즐겨찾기) 이후는 Out of Scope |

---

## 1. Overview

### 1.1 Design Goals

- README §3에 정의된 Router → Service → Repository → Database 4-Layer 구조를 그대로 구현한다.
- Google Places API는 별도 Client 계층으로 분리하여 Service가 Repository(PostgreSQL)와 Client(Google API)를 조합하게 한다.
- 인증 없는 단일 사용자 기준으로, 불필요한 권한/세션 로직을 배제한다.

### 1.2 Design Principles

- **Single Responsibility**: Router는 HTTP 처리만, Service는 Business Logic만, Repository는 순수 CRUD 쿼리만 담당한다.
- **Keep It Simple** (README §9): Phase 1 범위를 벗어나는 추상화(예: Repository 인터페이스/DI 컨테이너)는 도입하지 않는다.
- **외부 의존성 격리**: Google Places API 호출은 `clients/google_places_client.py`에만 위치시켜, 이후 캐싱 도입 시 Service/Router 변경 없이 Client만 교체 가능하게 한다.

---

## Detailed Design

> §2(Architecture Options) ~ §4(API Specification)에 걸쳐 구조·데이터 모델·API 계약을 상세히 정의한다.

## 2. Architecture Options

### 2.0 Architecture Comparison

| Criteria | Option A: Minimal | Option B: Clean | Option C: Pragmatic |
|----------|:-:|:-:|:-:|
| **Approach** | Router가 Repository 직접 호출 | Tag/Places 완전 분리 | README 4-Layer, Tag는 restaurant_service에 포함 |
| **New Files** | 6 | 12 | 9 |
| **Modified Files** | 0 | 0 | 0 |
| **Complexity** | Low | High | Medium |
| **Maintainability** | Medium | High | High |
| **Effort** | Low | High | Medium |
| **Risk** | Low (Business Logic이 Router에 섞임) | Low (Phase 1 규모 대비 과설계) | Low (균형) |
| **Recommendation** | Quick wins, hotfixes | Long-term projects | **Default choice** |

**Selected**: Option C — Pragmatic Balance — **Rationale**: README에 명시된 4-Layer 구조를 그대로 따르면서, Tag는 Restaurant에 종속적인 개념(N:M 부속 데이터)이므로 별도 Service로 분리하지 않고 `restaurant_service` 내에서 처리한다. Google Places는 외부 시스템이므로 독립된 Router(`places.py`)/Service/Client로 분리한다. 사용자 확정 사항.

> 아래 상세 설계는 Option C를 따른다.

### 2.1 Component Diagram

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI App     │────▶│ PostgreSQL  │
│ (Frontend)  │     │ Router/Service/    │     │  (restaurants,│
│             │     │ Repository         │     │   tags, ...)  │
└─────────────┘     └──────────────────┘     └─────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Google Places    │
                    │  Client (HTTP)    │
                    └──────────────────┘
```

### 2.2 Data Flow

```
[Restaurant 생성]
User Input (google_place_id 등) → Router 검증(Pydantic)
  → restaurant_service.create_restaurant()
      → tag 처리(존재하면 재사용, 없으면 생성)
      → restaurant_repository.create()
  → Response (RestaurantResponse)

[Places 검색]
User Query → Router 검증 → google_places_service.search()
  → google_places_client.search_places() (Google API 직접 호출)
  → Response (PlaceCandidate[])
```

### 2.3 Dependencies

| Component | Depends On | Purpose |
|-----------|-----------|---------|
| `routers/restaurants.py` | `services/restaurant_service.py` | Restaurant CRUD 요청 위임 |
| `routers/places.py` | `services/google_places_service.py` | Places 검색 요청 위임 |
| `services/restaurant_service.py` | `repositories/restaurant_repository.py`, `repositories/tag_repository.py` | DB 조작 위임, 태그 연결 처리 |
| `services/google_places_service.py` | `clients/google_places_client.py` | 외부 API 호출 위임 |
| `repositories/*` | `core/database.py` (SQLAlchemy Session) | DB 접근 |
| `clients/google_places_client.py` | `core/config.py` (`GOOGLE_PLACES_API_KEY`) | 인증 키 조회 |

---

## 3. Data Model

### 3.1 Entity Definition

```python
# app/models/restaurant.py
class Restaurant(Base):
    __tablename__ = "restaurants"

    id: int                    # PK, autoincrement
    google_place_id: str        # Google Places Place ID, unique
    name: str
    address: str
    latitude: float
    longitude: float
    status: RestaurantStatus    # VISITED | WANT_TO_GO (enum)
    my_rating: int | None        # 1~5, nullable
    memo: str | None
    created_at: datetime
    updated_at: datetime

    tags: list["Tag"]            # via restaurant_tags (N:M)


# app/models/tag.py
class Tag(Base):
    __tablename__ = "tags"

    id: int          # PK
    name: str         # unique


# restaurant_tags — association table (no separate model class needed)
```

### 3.2 Entity Relationships

```
[Restaurant] N ──── M [Tag]   (via restaurant_tags)
```

### 3.3 Database Schema

```sql
CREATE TYPE restaurant_status AS ENUM ('VISITED', 'WANT_TO_GO');

CREATE TABLE restaurants (
    id BIGSERIAL PRIMARY KEY,
    google_place_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    status restaurant_status NOT NULL,
    my_rating SMALLINT CHECK (my_rating BETWEEN 1 AND 5),
    memo TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE restaurant_tags (
    restaurant_id BIGINT NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (restaurant_id, tag_id)
);

CREATE INDEX idx_restaurants_status ON restaurants(status);
```

> `ON DELETE CASCADE`로 Restaurant 삭제 시 `restaurant_tags` 고아 레코드가 자동 제거된다 (Plan §5 Risk 대응, FR-05).

---

## 4. API Specification

### 4.1 Endpoint List

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /restaurants | 목록 조회 (status 필터 지원) | None |
| GET | /restaurants/{restaurant_id} | 단건 조회 | None |
| POST | /restaurants | 생성 | None |
| PATCH | /restaurants/{restaurant_id} | 부분 수정 | None |
| DELETE | /restaurants/{restaurant_id} | Hard delete | None |
| GET | /places/search | Google Places 검색 프록시 | None |

### 4.2 Detailed Specification

#### `GET /restaurants?status={VISITED|WANT_TO_GO}`

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "google_place_id": "ChIJ...",
      "name": "이치란 라멘",
      "address": "도쿄도 시부야구...",
      "latitude": 35.6595,
      "longitude": 139.7005,
      "status": "VISITED",
      "my_rating": 5,
      "memo": "돈코츠 최고",
      "tags": ["라멘", "일본"],
      "created_at": "2026-09-08T00:00:00Z",
      "updated_at": "2026-09-08T00:00:00Z"
    }
  ]
}
```

#### `POST /restaurants`

**Request:**
```json
{
  "google_place_id": "ChIJ...",
  "name": "이치란 라멘",
  "address": "도쿄도 시부야구...",
  "latitude": 35.6595,
  "longitude": 139.7005,
  "status": "WANT_TO_GO",
  "my_rating": null,
  "memo": null,
  "tags": ["라멘", "일본"]
}
```

**Response (201 Created):** 생성된 Restaurant 객체 (§4.2 GET 응답과 동일 shape)

**Error Responses:**
- `400 Bad Request`: 필수 필드 누락, status 값이 enum 외의 값
- `409 Conflict`: `google_place_id` 중복 (이미 등록된 장소)

#### `PATCH /restaurants/{restaurant_id}`

**Request** (모든 필드 optional, 제공된 필드만 수정):
```json
{
  "status": "VISITED",
  "my_rating": 4,
  "memo": "재방문 의사 있음",
  "tags": ["라멘"]
}
```

**Response (200 OK):** 수정된 Restaurant 객체

**Error Responses:**
- `404 Not Found`: 존재하지 않는 restaurant_id

**`tags` 필드 처리 정책**: `tags`가 요청 body에 포함되면 **전체 교체(replace)**로 처리한다. 즉, 요청에 담긴 태그 목록이 해당 restaurant의 최종 태그 목록이 되며(기존 매핑을 모두 삭제 후 재생성), 부분 추가/삭제는 지원하지 않는다. `tags` 필드 자체가 요청 body에 없으면 기존 태그를 그대로 유지한다.

#### `DELETE /restaurants/{restaurant_id}`

**Response (204 No Content)**

**Error Responses:**
- `404 Not Found`: 존재하지 않는 restaurant_id

#### `GET /places/search?query={text}`

**Response (200 OK):**
```json
{
  "data": [
    {
      "google_place_id": "ChIJ...",
      "name": "이치란 라멘",
      "address": "도쿄도 시부야구...",
      "latitude": 35.6595,
      "longitude": 139.7005
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request`: `query` 파라미터 누락
- `502 Bad Gateway`: Google Places API 호출 실패 (Client 예외를 Service가 변환)

**재시도 정책**: `google_places_client`는 재시도를 수행하지 않는다(no retry). 타임아웃(5초)이나 오류 발생 시 즉시 예외를 발생시켜 Service가 502로 변환한다. Phase 1은 단일 사용자 수동 요청이므로, 실패 시 사용자가 검색을 다시 시도하는 것으로 충분하며 재시도 로직 도입은 과설계로 판단한다.

---

## 5. UI/UX Design

> 본 Repository는 Backend API 전용이며 UI는 `my-food-map-frontend` Repository에서 별도로 구현된다. 본 섹션은 해당 없음(N/A).

---

## 6. Error Handling

### 6.1 Error Code Definition

| Code | Message | Cause | Handling |
|------|---------|-------|----------|
| 400 | Invalid input | Pydantic validation 실패 | 클라이언트에 field 단위 에러 반환 |
| 404 | Restaurant not found | 존재하지 않는 restaurant_id | 404 반환, 재조회 유도 |
| 409 | Duplicate google_place_id | 이미 등록된 장소 재등록 시도 | 기존 레코드 안내 |
| 502 | Google Places API error | 외부 API 타임아웃/오류 | Client 예외를 Service에서 502로 변환, 원인 로깅 |
| 500 | Internal error | 예상치 못한 서버 오류 | 에러 로깅, 사용자에게는 일반 메시지만 노출 |

### 6.2 Error Response Format

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Restaurant not found",
    "details": {}
  }
}
```

---

## 7. Security Considerations

- [x] Input validation: Pydantic Schema로 모든 요청 본문/쿼리 파라미터 검증
- [ ] Authentication/Authorization: Phase 1 범위 아님 — Plan §7.2에서 단일 사용자/인증 없음으로 사용자 확정. 근거: 서비스 소유자 본인만 사용하는 개인용 도구이며(Context Anchor WHO), 다중 사용자 지원은 Phase 2 이후 스코프
- [x] Sensitive data 보호: `GOOGLE_PLACES_API_KEY`는 환경변수로만 관리, 응답 body에 노출 금지
- [ ] HTTPS enforcement: 로컬 개발 단계 미적용 — 근거: Phase 1은 로컬/개인 환경에서만 구동되며, 배포 시점의 HTTPS 적용은 Infrastructure Repository(리버스 프록시/인증서 관리) 책임 범위로, 본 Backend Repository의 애플리케이션 코드 변경 없이 처리 가능
- [ ] Rate Limiting: Phase 1 범위 아님 — 근거: 단일 사용자가 개인 용도로만 호출하므로 남용(abuse) 시나리오가 존재하지 않음. 다만 Google Places API 자체의 쿼터 초과는 502로 노출되므로(§6.1) 별도 완화 없음

---

## 8. Test Plan

### 8.1 Test Scope

| Type | Target | Tool | Phase |
|------|--------|------|-------|
| L1: API Tests | `/restaurants`, `/places/search` 엔드포인트 | pytest + httpx (FastAPI TestClient) | Do |
| L2: UI Action Tests | 해당 없음 (Backend 전용 Repository) | - | - |
| L3: E2E Scenario Tests | 해당 없음 (Frontend Repository에서 별도 수행) | - | - |

### 8.2 L1: API Test Scenarios

| # | Endpoint | Method | Test Description | Expected Status | Expected Response |
|---|----------|--------|-----------------|:--------------:|-------------------|
| 1 | /restaurants | GET | 전체 목록 조회 | 200 | `.data`는 배열 |
| 2 | /restaurants?status=VISITED | GET | status 필터 적용 | 200 | 결과 전부 `status == "VISITED"` |
| 3 | /restaurants/{id} | GET | 존재하는 id 단건 조회 | 200 | `.data.id`가 요청 id와 일치 |
| 4 | /restaurants/{id} | GET | 존재하지 않는 id 조회 | 404 | `.error.code == "NOT_FOUND"` |
| 5 | /restaurants | POST | 유효한 데이터로 생성 | 201 | `.id` 존재, DB에 row 생성 확인 |
| 6 | /restaurants | POST | 필수 필드 누락 | 400 | `.error.details`에 필드 에러 |
| 7 | /restaurants | POST | 중복 google_place_id | 409 | `.error.code == "CONFLICT"` |
| 8 | /restaurants/{id} | PATCH | status/my_rating/memo 부분 수정 | 200 | 수정된 필드만 반영, 나머지 유지 |
| 9 | /restaurants/{id} | DELETE | 존재하는 id 삭제 | 204 | 이후 GET 시 404, restaurant_tags에도 row 없음 |
| 10 | /restaurants/{id} | DELETE | 존재하지 않는 id 삭제 | 404 | `.error.code == "NOT_FOUND"` |
| 11 | /places/search?query=라멘 | GET | 정상 검색 (Google API mock) | 200 | `.data`는 배열, 각 항목에 google_place_id 포함 |
| 12 | /places/search | GET | query 파라미터 누락 | 400 | `.error.details`에 필드 에러 |
| 13 | /places/search?query=x | GET | Google API 실패 시뮬레이션 | 502 | `.error.code == "EXTERNAL_API_ERROR"` |

### 8.3 L2: UI Action Test Scenarios

N/A — 본 Repository는 UI를 포함하지 않는다.

### 8.4 L3: E2E Scenario Test Scenarios

N/A — Frontend 연동 E2E는 `my-food-map-frontend` Repository 또는 통합 테스트 환경에서 별도 진행한다. Phase 1 Success Criteria의 "Frontend와 연결되어 정상 동작"은 Do 단계 완료 후 수동 통합 테스트로 확인한다.

### 8.5 Seed Data Requirements

| Entity | Minimum Count | Key Fields Required |
|--------|:------------:|---------------------|
| restaurants | 3 | status에 VISITED 1건 이상, WANT_TO_GO 1건 이상 포함 |
| tags | 2 | name 유니크 |
| restaurant_tags | 2 | 최소 1개 restaurant가 2개 이상 tag를 가지도록 구성 (N:M 검증) |

---

## 9. Clean Architecture

### 9.1 Layer Structure

| Layer | Responsibility | Location |
|-------|---------------|----------|
| **Router** | HTTP Request/Response, Pydantic 검증, Status Code | `app/routers/` |
| **Service** | Business Logic, VISITED/WANT_TO_GO 처리, Google/Personal 데이터 조합 | `app/services/` |
| **Repository** | Database CRUD, SQLAlchemy Query | `app/repositories/` |
| **Client** | 외부 API 통신 (Google Places API) | `app/clients/` |

### 9.2 Dependency Rules

```
┌─────────────────────────────────────────────────────────────┐
│                    Dependency Direction                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Router ──→ Service ──→ Repository ──→ Database             │
│                  │                                          │
│                  └──→ Client ──→ Google Places API            │
│                                                             │
│   Rule: Router는 Repository/Client를 직접 호출하지 않는다      │
│         Repository는 Client를 호출하지 않는다 (역할 분리 유지) │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 File Import Rules

| From | Can Import | Cannot Import |
|------|-----------|---------------|
| Router | Service, Schema | Repository, Client, Model 직접 |
| Service | Repository, Client, Schema, Model | Router |
| Repository | Model, Database session | Service, Router, Client |
| Client | Core config | Service, Router, Repository |

### 9.4 This Feature's Layer Assignment

| Component | Layer | Location |
|-----------|-------|----------|
| `restaurants_router` | Router | `app/routers/restaurants.py` |
| `places_router` | Router | `app/routers/places.py` |
| `restaurant_service` (Restaurant CRUD + Tag 처리) | Service | `app/services/restaurant_service.py` |
| `google_places_service` | Service | `app/services/google_places_service.py` |
| `restaurant_repository` | Repository | `app/repositories/restaurant_repository.py` |
| `tag_repository` | Repository | `app/repositories/tag_repository.py` |
| `google_places_client` | Client | `app/clients/google_places_client.py` |
| `Restaurant`, `Tag` 모델 | Model | `app/models/restaurant.py`, `app/models/tag.py` |
| `RestaurantCreate/Update/Response` 스키마 | Schema | `app/schemas/restaurant.py` |
| `RestaurantStatus` enum | Enum | `app/enums/restaurant_status.py` |

---

## 10. Coding Convention Reference

> Phase 2 Pipeline(`docs/01-plan/conventions.md`)이 아직 없으므로, 본 Design에서 Python/FastAPI 표준 컨벤션을 우선 정의한다. 이후 Phase 2 진행 시 본 섹션을 참조하여 공식 컨벤션 문서로 승격한다.

### 10.1 Naming Conventions

| Target | Rule | Example |
|--------|------|---------|
| 함수/변수 | snake_case | `get_restaurant_by_id()`, `my_rating` |
| 클래스 (Model/Schema) | PascalCase | `Restaurant`, `RestaurantCreate` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RATING`, `DEFAULT_PAGE_SIZE` |
| 파일 | snake_case.py | `restaurant_service.py` |
| 폴더 | snake_case | `routers/`, `repositories/` |

### 10.2 Import Order

```python
# 1. 표준 라이브러리
from datetime import datetime

# 2. 서드파티 라이브러리
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

# 3. 로컬 절대 임포트 (app 기준)
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse
from app.services.restaurant_service import RestaurantService
```

### 10.3 Environment Variables

| Prefix/Name | Purpose | Scope |
|--------|---------|-------|
| `DATABASE_URL` | PostgreSQL 연결 문자열 | Server |
| `GOOGLE_PLACES_API_KEY` | Google Places API 인증 키 | Server |
| `APP_ENV` | 실행 환경 구분 (local/dev/prod) | Server |

### 10.4 This Feature's Conventions

| Item | Convention Applied |
|------|-------------------|
| Router 응답 | Pydantic `response_model` 명시, envelope 없이 FastAPI 기본 구조 사용 (단, 목록 조회는 `{"data": [...]}` 형태 유지) |
| 에러 처리 | `HTTPException` + `app/core/exceptions.py`의 커스텀 예외(`RestaurantNotFoundError`, `ExternalApiError`) |
| DB 세션 | FastAPI `Depends(get_db)` 로 Router에 주입, Service/Repository로 전달 |

---

## Implementation Order

> See §11.2 below for the ordered implementation checklist.

## 11. Implementation Guide

### 11.1 File Structure

```
app/
├── main.py
├── routers/
│   ├── restaurants.py
│   └── places.py
├── schemas/
│   └── restaurant.py
├── models/
│   ├── restaurant.py
│   └── tag.py
├── repositories/
│   ├── restaurant_repository.py
│   └── tag_repository.py
├── services/
│   ├── restaurant_service.py
│   └── google_places_service.py
├── clients/
│   └── google_places_client.py
├── core/
│   ├── config.py
│   ├── database.py
│   └── exceptions.py
└── enums/
    └── restaurant_status.py
```

### 11.2 Implementation Order

1. [ ] `core/config.py`, `core/database.py` — 환경변수 로딩 및 DB 연결 설정
2. [ ] `enums/restaurant_status.py`, `models/restaurant.py`, `models/tag.py` — 데이터 모델 정의
3. [ ] Alembic migration 또는 초기 DDL 스크립트 작성 (§3.3 스키마 반영)
4. [ ] `schemas/restaurant.py` — Pydantic 스키마 (Create/Update/Response)
5. [ ] `repositories/restaurant_repository.py`, `repositories/tag_repository.py`
6. [ ] `clients/google_places_client.py` — Google Places API 연동
7. [ ] `services/google_places_service.py`, `services/restaurant_service.py`
8. [ ] `routers/restaurants.py`, `routers/places.py`, `main.py` 등록
9. [ ] pytest 테스트 작성 (§8.2 시나리오 기반)

### 11.3 Session Guide

#### Module Map

| Module | Scope Key | Description | Estimated Turns |
|--------|-----------|-------------|:---------------:|
| Core & Data Model | `module-1` | config, database, models, enum, DDL | 15-20 |
| Repository & Schema | `module-2` | restaurant/tag repository, Pydantic schema | 15-20 |
| Google Places 연동 | `module-3` | client, google_places_service, places router | 15-20 |
| Restaurant Service & Router | `module-4` | restaurant_service(태그 처리 포함), restaurants router | 20-25 |
| Tests | `module-5` | pytest L1 API 테스트 (§8.2) | 20-25 |

#### Recommended Session Plan

| Session | Phase | Scope | Turns |
|---------|-------|-------|:-----:|
| Session 1 | Plan + Design | 전체 | 완료 |
| Session 2 | Do | `--scope module-1,module-2` | 30-40 |
| Session 3 | Do | `--scope module-3,module-4` | 35-45 |
| Session 4 | Do | `--scope module-5` | 20-25 |
| Session 5 | Check + Report | 전체 | 30-40 |

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-09-08 | Initial draft | SY LEE |
| 0.2 | 2026-09-10 | PATCH `tags` 교체 정책, Google Places 재시도 정책(no retry), §7 Security 근거 보완 | SY LEE |

---
template: plan
version: 1.3
description: PDCA Plan phase document template with Context Anchor and Architecture considerations
variables:
  - feature: restaurant-mvp
  - date: 2026-09-08
  - author: SY LEE
  - project: my-food-map-backend
  - version: 0.1.0
---

# restaurant-mvp Planning Document

> **Summary**: Google Places 장소 데이터와 개인 방문 기록(VISITED/WANT_TO_GO, 평점, 메모, 태그)을 결합한 개인 맛집 지도 서비스의 Phase 1 MVP Backend API.
>
> **Project**: my-food-map-backend
> **Version**: 0.1.0
> **Author**: SY LEE
> **Date**: 2026-09-08
> **Status**: Draft

---

## Executive Summary

| Perspective | Content |
|-------------|---------|
| **Problem** | 방문했거나 방문하고 싶은 맛집을 개인적으로 기록·관리할 방법이 없고, Google Maps만으로는 개인 평점/메모/태그 같은 개인화 데이터를 남길 수 없다 |
| **Solution** | Google Places API로 장소 데이터를 검색·조회하고, Backend가 별도로 VISITED/WANT_TO_GO 상태·평점·메모·태그를 저장하는 Restaurant CRUD API를 4-Layer(Router→Service→Repository→Database) 구조로 구현한다 |
| **Function/UX Effect** | Frontend에서 지도 위에 저장된 맛집을 Marker로 표시하고, 상태별 필터링(방문함/가고싶음)과 개인 메모·평점·태그 관리가 가능해진다 |
| **Core Value** | Google의 정확한 장소 데이터 + 나만의 방문 기록을 결합한 개인 맛집 데이터베이스, 인증 없이 개인용으로 단순하게 사용 가능 |

---

## Context Anchor

> Auto-generated from Executive Summary. Propagated to Design/Do documents for context continuity.

| Key | Value |
|-----|-------|
| **WHY** | 개인이 방문/관심 맛집을 지도 기반으로 기록하고 개인 데이터(평점, 메모, 태그)를 관리할 수단이 없음 |
| **WHO** | 서비스 소유자 본인 (단일 사용자, 인증 없음) |
| **RISK** | Google Places API 매 검색 직접 호출로 인한 API 비용 증가 및 응답 지연 |
| **SUCCESS** | Restaurant CRUD API 동작 + Google Places 검색 연계 + VISITED/WANT_TO_GO 상태 관리 + Frontend 연동 정상 동작 |
| **SCOPE** | Phase 1(MVP)만 포함, Phase 2(방문 기록/즐겨찾기) 이후는 Out of Scope |

---

## 1. Overview

### 1.1 Purpose

Google Maps Platform이 제공하는 장소 데이터(Place ID, 이름, 주소, 좌표)와 서비스가 직접 관리하는 개인 데이터(VISITED/WANT_TO_GO, 평점, 메모, 태그)를 결합하여, 개인 맛집 지도 서비스의 Backend API(Phase 1 MVP)를 제공한다.

### 1.2 Background

my-food-map은 한국과 일본을 중심으로 방문했던 맛집과 방문하고 싶은 가게를 지도 위에 기록·관리하는 개인 프로젝트다. Frontend(지도/UI)와 Infrastructure(배포)는 별도 Repository로 분리되어 있으며, 본 Repository는 API/Business Logic/Database를 담당한다. 이 프로젝트의 목적 중 하나는 Frontend 학습이므로 Backend는 필요 이상으로 복잡하게 만들지 않는다.

### 1.3 Related Documents

- Requirements: `README.md` (본 Repository 루트)
- References: 관련 Repository — `my-food-map-frontend`, `my-food-map-infrastructure`

---

## 2. Scope

### 2.1 In Scope

- [ ] Restaurant CRUD API (`GET/POST/PATCH/DELETE /restaurants`, `GET /restaurants/{id}`)
- [ ] Google Places 검색 연계 (Google Places API 직접 호출, 캐싱 없음)
- [ ] VISITED / WANT_TO_GO 상태 관리 및 status 필터 (`GET /restaurants?status=`)
- [ ] 개인 평점(my_rating) / 메모(memo) / 태그(tag) 저장 및 N:M 태그 관계 (restaurants, tags, restaurant_tags 테이블)
- [ ] Restaurant Hard Delete (실제 row 삭제)
- [ ] 4-Layer 아키텍처 스캐폴딩 (Router → Service → Repository → Database, 외부 API는 Client 경유)

### 2.2 Out of Scope

- 방문 기록 관리 (`restaurant_visits`, Phase 2)
- 즐겨찾기, 가격대, 카테고리, List View (Phase 2)
- 현재 위치 기반 검색, 지도 영역 조회, PostGIS, Marker Cluster (Phase 3)
- 방문 통계, 추천, Heatmap (Phase 4)
- 로그인/인증, 멀티 사용자, 공유, 사진 업로드 (Phase 5)
- Google Places 검색 결과 캐싱

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-01 | `POST /restaurants`로 Google Place 정보 + 개인 데이터(status, my_rating, memo, tags)를 받아 Restaurant 생성 | High | Pending |
| FR-02 | `GET /restaurants`로 전체 Restaurant 목록 조회, `status` 쿼리 파라미터로 필터링(VISITED/WANT_TO_GO) | High | Pending |
| FR-03 | `GET /restaurants/{restaurant_id}`로 단건 조회 | High | Pending |
| FR-04 | `PATCH /restaurants/{restaurant_id}`로 status, my_rating, memo, tags 등 개인 데이터 부분 수정 | High | Pending |
| FR-05 | `DELETE /restaurants/{restaurant_id}`로 Restaurant Hard Delete (연관 restaurant_tags도 함께 삭제) | High | Pending |
| FR-06 | Google Places 검색 API를 Backend가 프록시하여 장소 후보(Place ID, 이름, 주소, 좌표) 반환 | High | Pending |
| FR-07 | Tag는 이름 기준으로 존재하면 재사용, 없으면 생성 후 restaurant_tags에 N:M 연결 | Medium | Pending |

### 3.2 Non-Functional Requirements

| Category | Criteria | Measurement Method |
|----------|----------|-------------------|
| Simplicity | 인증/멀티 사용자 로직 없이 단일 사용자 기준 유지 (README 9절 원칙) | 코드 리뷰 시 인증 관련 코드 부재 확인 |
| Error Handling | Google Places API 실패 시 500이 아닌 명확한 에러 메시지로 응답 | 통합 테스트로 외부 API 실패 시나리오 검증 |
| Data Integrity | Restaurant 삭제 시 restaurant_tags 고아 레코드 미발생 | FK CASCADE 또는 트랜잭션 처리 확인 |

---

## 4. Success Criteria

### 4.1 Definition of Done

- [ ] Restaurant CRUD API 5개 엔드포인트 모두 구현 및 동작
- [ ] Google Places 검색 연계 API 동작 (Place ID/이름/주소/좌표 반환)
- [ ] VISITED/WANT_TO_GO 상태 관리 및 status 필터 동작
- [ ] 개인 평점/메모/태그 저장 및 조회 동작 (N:M 태그 관계 포함)
- [ ] Frontend와 연결되어 정상 동작 확인
- [ ] Unit/Integration 테스트 작성 및 통과
- [ ] Code review 완료

### 4.2 Quality Criteria

- [ ] 신규 코드 테스트 커버리지 80% 이상
- [ ] Lint 오류 0건
- [ ] Docker 기반 로컬 빌드/실행 성공

---

## 5. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Google Places API 매 요청 직접 호출로 인한 비용 증가 | Medium | Medium | Phase 1은 개인 사용 규모로 트래픽이 적어 우선 수용, 사용량 증가 시 Phase 2에서 캐싱 도입 검토 |
| Google Places API 키 유출/설정 누락 | High | Low | API Key는 환경변수로만 관리, `.env`는 `.gitignore`에 포함, 서버 기동 시 필수 환경변수 존재 검증 |
| 인증 없는 구조에서 향후 멀티 사용자 확장 시 스키마 변경 필요 | Medium | Medium | Phase 5로 명시적으로 분리되어 있어 현재는 수용, 확장 시 restaurants에 user_id 컬럼 추가하는 방식으로 대응 |
| 외부 API(Google Places) 장애 시 Restaurant 생성 흐름 전체 실패 | Medium | Low | Client 레이어에서 예외를 명확히 구분해 Service가 사용자 친화적 에러로 변환 |

---

## 6. Impact Analysis

> 신규 프로젝트 초기 구축(Phase 1 MVP)으로, 기존 운영 중인 리소스가 없어 본 섹션은 대부분 해당 없음(N/A) 처리한다.

### 6.1 Changed Resources

| Resource | Type | Change Description |
|----------|------|--------------------|
| `restaurants` 테이블 | DB Model | 신규 생성 (id, google_place_id, name, address, latitude, longitude, status, my_rating, memo, created_at, updated_at) |
| `tags` 테이블 | DB Model | 신규 생성 (id, name) |
| `restaurant_tags` 테이블 | DB Model | 신규 생성 (restaurant_id, tag_id, N:M 연결) |
| `/restaurants` API | API | 신규 생성 (GET/POST/PATCH/DELETE, 필터링 포함) |

### 6.2 Current Consumers

신규 프로젝트이므로 기존 Consumer가 없다. Frontend Repository(`my-food-map-frontend`)가 최초 Consumer가 될 예정이며, API 계약(Contract)은 본 Plan의 §3.1과 README §6을 기준으로 한다.

| Resource | Operation | Code Path | Impact |
|----------|-----------|-----------|--------|
| `/restaurants` | CREATE/READ/UPDATE/DELETE | my-food-map-frontend (미구현) | None (신규 API, 기존 Consumer 없음) |

### 6.3 Verification

- [x] 기존 Consumer 없음 확인 (신규 프로젝트)
- [ ] Frontend와 API 계약(Request/Response 스키마) 합의 완료
- [ ] Frontend 연동 테스트로 정상 동작 확인 (Phase 1 완료 기준)

---

## 7. Architecture Considerations

### 7.1 Project Level Selection

| Level | Characteristics | Recommended For | Selected |
|-------|-----------------|-----------------|:--------:|
| **Starter** | Simple structure (`components/`, `lib/`, `types/`) | Static sites, portfolios, landing pages | ☐ |
| **Dynamic** | Feature-based modules, BaaS integration (bkend.ai) | Web apps with backend, SaaS MVPs, fullstack apps | ☑ |
| **Enterprise** | Strict layer separation, DI, microservices | High-traffic systems, complex architectures | ☐ |

> 본 프로젝트는 자체 FastAPI Backend를 직접 구축하는 방식으로, bkend.ai BaaS는 사용하지 않는다. README에 명시된 Router→Service→Repository→Database 4-Layer 구조를 Dynamic 수준의 실용적 기준으로 채택한다.

### 7.2 Key Architectural Decisions

| Decision | Options | Selected | Rationale |
|----------|---------|----------|-----------|
| Framework | FastAPI / Flask / Django | FastAPI | README Tech Stack에 명시, 비동기 지원 및 Pydantic 기반 자동 검증 |
| ORM | SQLAlchemy / Tortoise ORM | SQLAlchemy | README Tech Stack에 명시 |
| Validation | Pydantic / Marshmallow | Pydantic | README Tech Stack에 명시, FastAPI와 통합 |
| Database | PostgreSQL / SQLite | PostgreSQL | README Tech Stack에 명시, Phase 3 PostGIS 확장 고려 |
| 외부 API 연계 | 직접 호출 / 캐싱 | Client 레이어에서 직접 호출 (캐싱 없음) | Phase 1 단순성 원칙, 사용자 확정 |
| 인증 | 없음 / 간단 인증 | 없음 | 개인용 단일 사용자, Phase 5로 확장 예정, 사용자 확정 |
| 삭제 정책 | Hard delete / Soft delete | Hard delete | README에 soft delete 언급 없음, MVP 단순성 원칙, 사용자 확정 |
| Backend | BaaS (bkend.ai) / Custom Server | Custom Server (FastAPI) | README에 자체 Repository/Architecture로 명시되어 있어 BaaS 미해당 |

### 7.3 Clean Architecture Approach

```
Selected Level: Dynamic (Custom FastAPI, README 4-Layer 구조 적용)

Folder Structure Preview:
┌─────────────────────────────────────────────────────┐
│ app/                                                 │
│   main.py                                            │
│   routers/       restaurants.py, visits.py, tags.py  │
│   schemas/       restaurant.py, visit.py, tag.py      │
│   models/        restaurant.py, visit.py, tag.py      │
│   repositories/  restaurant_repository.py, ...        │
│   services/      restaurant_service.py,               │
│                   google_places_service.py            │
│   clients/       google_places_client.py              │
│   core/          config.py, database.py               │
│   enums/         restaurant_status.py                 │
└─────────────────────────────────────────────────────┘
```

---

## 8. Convention Prerequisites

### 8.1 Existing Project Conventions

- [ ] `CLAUDE.md`가 코딩 컨벤션 섹션을 포함 (프로젝트 루트에 아직 없음, 사용자 글로벌 CLAUDE.md만 존재)
- [ ] `docs/01-plan/conventions.md` 존재 (Phase 2 Pipeline 산출물, 아직 없음)
- [ ] `CONVENTIONS.md` 프로젝트 루트에 존재 (아직 없음)
- [ ] Lint 설정 (`ruff`/`flake8` 등, 아직 없음)
- [ ] Formatter 설정 (`black`/`ruff format` 등, 아직 없음)
- [ ] `pyproject.toml` (README 구조에 명시되어 있으나 아직 미생성)

### 8.2 Conventions to Define/Verify

| Category | Current State | To Define | Priority |
|----------|---------------|-----------|:--------:|
| **Naming** | missing | Python 표준(PEP 8): snake_case 함수/변수, PascalCase 클래스 | High |
| **Folder structure** | 존재(README §4에 명시) | README 구조를 그대로 채택, 신규 모듈 추가 시 동일 패턴 유지 | High |
| **Import order** | missing | 표준 라이브러리 → 서드파티 → 로컬(app.*) 순서, isort 규칙 | Medium |
| **Environment variables** | missing | `.env` 기반, §8.3 목록 참고 | Medium |
| **Error handling** | missing | FastAPI `HTTPException` + 커스텀 예외 클래스로 Service/Client 계층 에러 구분 | Medium |

### 8.3 Environment Variables Needed

| Variable | Purpose | Scope | To Be Created |
|----------|---------|-------|:-------------:|
| `DATABASE_URL` | PostgreSQL 연결 문자열 | Server | ☑ |
| `GOOGLE_PLACES_API_KEY` | Google Places API 인증 키 | Server | ☑ |
| `APP_ENV` | 실행 환경 구분 (local/dev/prod) | Server | ☑ |

### 8.4 Pipeline Integration

| Phase | Status | Document Location | Command |
|-------|:------:|-------------------|---------|
| Phase 1 (Schema) | ☐ | `docs/01-plan/schema.md` | `/pipeline-next` |
| Phase 2 (Convention) | ☐ | `docs/01-plan/conventions.md` | `/pipeline-next` |

---

## 9. Next Steps

1. [ ] Design 문서 작성 (`restaurant-mvp.design.md`) — API 계약 상세, DB 스키마 DDL, 4-Layer 세부 설계
2. [ ] Frontend와 API 계약(Request/Response 스키마) 리뷰 및 합의
3. [ ] FastAPI 프로젝트 스캐폴딩 및 구현 시작

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-09-08 | Initial draft | SY LEE |

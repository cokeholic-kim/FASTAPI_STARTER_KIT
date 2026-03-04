# FastAPI Starter Kit

[![CI](https://github.com/cokeholic-kim/FASTAPI_STARTER_KIT/actions/workflows/ci.yml/badge.svg)](https://github.com/cokeholic-kim/FASTAPI_STARTER_KIT/actions/workflows/ci.yml)

## 개요

이 템플릿은 FastAPI 기반 스타터 키트로, 현재는 실제 동작이 보장된 최소 기능 세트를 기준으로 정리되어 있습니다.

- Python 3.12
- FastAPI + Pydantic V2
- SQLAlchemy 2.x (Async)
- PostgreSQL (asyncpg)
- pytest + pytest-asyncio

---

## 실행

```bash
cp .env.example .env
poetry install   # 또는 pip install -r requirements.txt
poetry run uvicorn app.main:app --reload --port 8000
```

- Health API: `http://localhost:8000/health`
- Docs: `http://localhost:8000/docs`

## API 계약 문서

- 최신 API 계약은 [docs/api-contract.md](docs/api-contract.md) 에 정리되어 있습니다.
- 주요 요청/응답 예시는 해당 문서의 `요청/응답 예시` 섹션에서 확인할 수 있습니다.

---

## 환경 설정

`.env`의 `DATABASE_URL`은 async 엔진(`create_async_engine`) 기준으로 설정합니다.

- 기본: `postgresql+asyncpg://postgres:password@localhost:5432/fastapi_db`
- 로컬 테스트/실험에서는 `sqlite+aiosqlite:///./fastapi_db.db`처럼 명시적으로 변경해서 사용

- 관측성
  - `PROMETHEUS_ENABLED=True` (기본값)

---

## 현재 구현 상태

- [x] 예외 미들웨어 (`AppException` -> `ErrorResponse`)
- [x] `/health` 라우트(헬스체크)
- [x] User 도메인 기본 CRUD
  - [x] `POST /users`
  - [x] `GET /users`
  - [x] `GET /users/{user_id}`
  - [x] `PUT /users/{user_id}`
  - [x] `DELETE /users/{user_id}`
- [x] 요청 로그/추적 미들웨어
  - [x] `X-Request-ID` 생성/전파
- [x] 에러 처리 미들웨어
  - [x] 공통 에러 응답(`ErrorResponse`) 및 `DUPLICATE/NOT_FOUND` 등의 상태 변환
- [x] 운영 관측성
  - [x] `/metrics` (Prometheus)
  - [x] `/observability/health`
  - [x] `/observability/request-metadata`
  - [x] 민감정보 마스킹(이메일/토큰/패스워드 계열)
  - [x] DB/배치 로그의 correlation-id 통합
- [x] 배치 예시 (`app/services/batch_job_example.py`)
- [x] Alembic 마이그레이션 기본 구조
- [x] GitHub Actions 기반 CI

### 구현 검증 상태

- [x] `tests/unit` (서비스 단위 테스트)
- [x] `tests/integration` (Health / Metrics / Observability / User API)
- [x] 중복 이메일 생성 처리 (409) 및 동시성 race-condition 보정
- [x] `DELETE /users/{id}` 204 No Content 응답
- [ ] 인증/인가 라우트 (로그인/토큰 갱신)

### 향후 구현 예정

- JWT 인증/권한(회원가입·로그인)
- 인증 기반 라우트 보호
- 사용자 도메인 기능 확장(프로필/권한/토큰 갱신 등)
- 운영용 배포 가이드 강화

---

## DB 마이그레이션

```bash
alembic upgrade head
alembic history
alembic downgrade -1
```

---

## 테스트/CI

```bash
poetry run pytest
poetry run pytest tests/unit
poetry run pytest tests/integration
poetry run pytest --cov=app --cov-report=html
```

실행 항목:

- 단위 테스트: `tests/unit`
- 통합 테스트: `tests/integration`

## 운영 관측성

- 로그
  - 요청 ID(`X-Request-ID`) 기반 JSON 구조화 로그
  - 민감정보 마스킹(이메일/비밀번호/토큰) 적용
- 연동 포인트
  - `GET /observability/request-metadata` (요청 메타 조회)
  - 배치 작업은 `app.utils.observability.batch_context`로 동일 `correlation_id`를 사용
- Prometheus 메트릭
  - `GET /metrics` 노출
  - 수집 대상: `http_requests_total`, `http_request_latency_seconds`, `http_requests_in_progress`
  - 요청 메타 지표는 내부 관측성 경로를 제외해 수집합니다.
    - 제외 경로: `/metrics`, `/observability/*`
- 배치 관측성 예시
  - `app/services/batch_job_example.py`에서 `batch_context`로 배치 작업의 `correlation_id`를 공통 로그 체인으로 묶는 예시 제공
  - 배치/잡 로그/DB 로그에서 동일 ID를 재사용하면 장애 추적이 쉬워집니다.

### GitHub Actions

`.github/workflows/ci.yml`은 `push`/`pull_request`를 `main`과 `master` 모두에서 실행하도록 설정되어 있습니다.

---

## 성능/구현 보강 포인트

- `UserRepository.list()`는 전체 행을 모두 적재해 개수를 구하지 않고, `COUNT(*)` 집계로 총 개수를 계산하도록 수정되었습니다.
- CI 브랜치가 `master`인 환경에서도 검증이 누락되지 않도록 워크플로우 트리거를 보강했습니다.
- 요청 단위 로그 전략(HTTP 미들웨어) 추가: `X-Request-ID` 생성/전파, 처리시간, 상태코드/요청 경로를 JSON 로그로 수집합니다.
- Prometheus 메트릭 수집을 위한 `/metrics` 엔드포인트와 요청 기반 `Counter/Histogram/Gauge` 미들웨어를 추가했습니다.
- 민감 정보 마스킹: 로그 이벤트에서 이메일/비밀번호/토큰류를 일괄 마스킹해 노출을 통제했습니다.
- 요청 메타 지표 전용 엔드포인트(`GET /observability/request-metadata`)를 추가해 헬스/메트릭 경로와 분리된 관측 채널을 구성했습니다.

---

## 폴더 구조

```text
.
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── observability.py
│   │   └── users.py
│   ├── middlewares/
│   │   ├── error_handler.py
│   │   ├── request_logging.py
│   │   └── metrics.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── response.py
│   │   └── user.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── observability.py
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── user.py
  │   │   └── batch_job_example.py
│   ├── __init__.py
│   └── main.py
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_create_users_table.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_health.py
│   │   ├── test_observability.py
│   │   ├── test_metrics.py
│   │   └── test_users.py
│   └── unit/
│       ├── __init__.py
│       └── test_user_service.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── api-contract.md
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── requirements-minimal.txt
├── pytest.ini
└── README.md
```

---

## 라이선스

MIT



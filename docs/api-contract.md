# API 계약 문서

이 문서는 현재 스타터킷에서 실제 동작하는 API 계약을 정리합니다.

## 공통 응답 포맷

- 성공 응답
  - 형식: `SuccessResponse`
  - 필드
    - `success`: `true`
    - `message`: 메시지(선택)
    - `data`: 응답 본문
    - `meta`: 부가 정보(선택)
- 실패 응답
  - 형식: `ErrorResponse`
  - 필드
    - `success`: `false`
    - `error_code`: 오류 코드
    - `message`: 오류 메시지
    - `details`: 세부 정보(선택)

## 인증/헤더

- 모든 요청은 `X-Request-ID`를 응답 헤더로 반환합니다.
- 에러 추적을 위해 로그/DB에서 `correlation_id`가 함께 기록됩니다.

## 엔드포인트

### Health

| Method | Path | 설명 | 응답 |
|---|---|---|---|
| GET | `/health` | 애플리케이션 상태 | 200 |

### User API

| Method | Path | 설명 | 요청 본문 | 응답(성공) | 주의 |
|---|---|---|---|---|---|
| POST | `/users` | 사용자 생성 | `email`, `name` | 201 + 생성 데이터 | 중복 이메일이면 409 |
| GET | `/users` | 사용자 목록/총건수 | `skip`, `limit`(쿼리) | 200 + `items`, `total` | `total`은 DB 집계로 계산 |
| GET | `/users/{user_id}` | 사용자 단건 조회 | - | 200 + 사용자 데이터 | 존재하지 않으면 404 |
| PUT | `/users/{user_id}` | 사용자 수정 | `name` 또는 `is_active` | 200 + 수정 데이터 | 존재하지 않으면 404 |
| DELETE | `/users/{user_id}` | 사용자 삭제 | - | 204 (본문 없음) | 존재하지 않으면 404 |

### 요청/응답 예시

#### 1) 사용자 생성

요청

```json
POST /users
{
  "email": "alice@example.com",
  "name": "Alice"
}
```

성공 응답

```json
{
  "success": true,
  "message": "User created",
  "data": {
    "id": 1,
    "email": "alice@example.com",
    "name": "Alice",
    "is_active": true,
    "created_at": "2026-03-05T00:00:00Z",
    "updated_at": "2026-03-05T00:00:00Z"
  }
}
```

중복 응답

```json
{
  "success": false,
  "error_code": "DUPLICATE",
  "message": "Email already exists",
  "details": {}
}
```

#### 2) 사용자 목록 조회

요청

```http
GET /users?skip=0&limit=10
```

성공 응답

```json
{
  "success": true,
  "message": "성공",
  "data": {
    "items": [
      {
        "id": 1,
        "email": "alice@example.com",
        "name": "Alice",
        "is_active": true,
        "created_at": "2026-03-05T00:00:00Z",
        "updated_at": "2026-03-05T00:00:00Z"
      }
    ],
    "total": 1
  }
}
```

#### 3) 삭제

요청

```http
DELETE /users/1
```

응답

- `204 No Content`
- Body: 없음

### Observability

| Method | Path | 설명 | 응답 |
|---|---|---|---|
| GET | `/metrics` | Prometheus 스크랩 포맷 | 200 |
| GET | `/observability/health` | 관측성 전용 건강 점검 | 200 |
| GET | `/observability/request-metadata` | 요청 메타 지표 | 200 |

## 에러 코드

| HTTP | error_code | 의미 |
|---|---|---|
| 400 | VALIDATION_ERROR | 요청 스키마/유효성 실패 |
| 401 | UNAUTHORIZED | 인증 필요 |
| 403 | FORBIDDEN | 권한 부족 |
| 404 | NOT_FOUND | 리소스 미존재 |
| 409 | DUPLICATE | 중복 데이터(예: 이메일) |
| 500 | INTERNAL_SERVER_ERROR | 서버 내부 오류 |

## 비고

- 요청 바디에서 `email`, `token`, `password`는 로그 마스킹 정책이 적용됩니다.

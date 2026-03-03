# 코드 작성 가이드

FastAPI 프로젝트의 코드 작성 표준과 가이드입니다.

## 목차
1. [아키텍처](#아키텍처)
2. [코드 스타일](#코드-스타일)
3. [폴더 구조](#폴더-구조)
4. [레이어별 작성 가이드](#레이어별-작성-가이드)
5. [API 응답 형식](#api-응답-형식)
6. [에러 핸들링](#에러-핸들링)
7. [테스트 작성](#테스트-작성)

---

## 아키텍처

### 레이어드 아키텍처
프로젝트는 다음과 같은 3계층 레이어드 아키텍처를 따릅니다:

```
Controller (라우트) → Service (비즈니스 로직) → Repository (데이터 접근)
```

**특징:**
- 각 계층은 단일 책임 원칙을 따릅니다
- 의존성 주입을 통해 결합도를 낮춥니다
- 테스트하기 쉬운 구조입니다

---

## 코드 스타일

### 기본 규칙
- **들여쓰기**: 4칸
- **라인 길이**: 최대 100자
- **네이밍**: camelCase (변수, 함수, 메서드)
- **상수**: UPPER_SNAKE_CASE

### 포매팅 도구
- **Black**: 자동 코드 포매팅
- **Ruff**: 린팅 및 정렬
- **mypy**: 타입 체킹

**자동 포매팅 실행:**
```bash
# Black 포매팅
black app/ tests/

# Ruff 린팅
ruff check app/ tests/

# mypy 타입 체킹
mypy app/

# 모두 한 번에 (pre-commit)
pre-commit run --all-files
```

### 주석 작성
- **비즈니스 로직에만** 한국어 주석 작성
- 함수/클래스 docstring은 한국어로 작성
- 명확한 코드는 주석 불필요

```python
def calculate_total_price(items: List[Item]) -> float:
    """주문의 총 가격을 계산한다"""
    # 할인율 적용 (VIP 회원 10% 할인)
    discount_rate = 0.1 if user.is_vip else 0
    return sum(item.price for item in items) * (1 - discount_rate)
```

---

## 폴더 구조

```
app/
├── core/                  # 설정 및 핵심 기능
│   ├── config.py         # 환경 설정
│   ├── database.py       # DB 연결
│   ├── logging.py        # 로깅 설정
│   └── exceptions.py     # 커스텀 예외
├── models/               # SQLAlchemy ORM 모델
│   ├── base.py          # 기본 모델
│   └── user.py          # User 모델
├── schemas/              # Pydantic DTO
│   ├── response.py      # 응답 형식
│   └── user.py          # User 요청/응답 DTO
├── controllers/          # 라우트 핸들러
│   ├── health.py        # 헬스 체크
│   └── user.py          # User 관련 라우트
├── services/             # 비즈니스 로직
│   └── user_service.py  # User 비즈니스 로직
├── repositories/         # DB 접근 계층
│   └── user_repository.py
├── middlewares/          # 미들웨어
│   └── error_handler.py
└── utils/                # 유틸리티 함수
    └── auth.py          # 인증 유틸

tests/
├── unit/                 # 단위 테스트
├── integration/          # 통합 테스트
└── conftest.py          # 테스트 설정

migrations/               # Alembic 마이그레이션
```

---

## 레이어별 작성 가이드

### 1. Controller (컨트롤러)

**책임:**
- 요청 수신 및 검증
- Service 호출
- 응답 반환

**작성 규칙:**
- 최소한의 로직만 포함
- 비즈니스 로직은 Service로 위임
- 20줄 이상이면 분리하기

```python
from fastapi import APIRouter, Depends
from app.services.user_service import UserService
from app.schemas.user import UserCreateRequest, UserResponse
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=SuccessResponse[UserResponse])
async def create_user(
    request: UserCreateRequest,
    service: UserService = Depends(),
) -> SuccessResponse[UserResponse]:
    """사용자 생성"""
    user = await service.create_user(request)
    return SuccessResponse(
        message="사용자가 생성되었습니다",
        data=UserResponse.from_model(user),
    ).to_response(status_code=201)
```

### 2. Service (서비스)

**책임:**
- 비즈니스 로직 구현
- Repository를 통한 데이터 접근
- 예외 처리

**작성 규칙:**
- DB 작업은 Repository로 위임
- 20줄 이상이면 함수 분리
- 트랜잭션 처리

```python
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest
from app.core.exceptions import DuplicateException


class UserService:
    def __init__(self, repository: UserRepository = Depends()):
        self.repository = repository

    async def create_user(self, request: UserCreateRequest):
        """사용자 생성"""
        # 중복 확인
        existing_user = await self._check_duplicate_email(request.email)
        if existing_user:
            raise DuplicateException("이미 등록된 이메일입니다")

        # 사용자 생성
        return await self.repository.create(request)

    async def _check_duplicate_email(self, email: str):
        """이메일 중복 확인"""
        return await self.repository.get_by_email(email)
```

### 3. Repository (저장소)

**책임:**
- 데이터 접근 계층
- SQL 쿼리 작성
- 데이터 변환

**작성 규칙:**
- 비즈니스 로직 없음 (CRUD만)
- 의존성 주입으로 Session 주입

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def create(self, data: UserCreateRequest) -> User:
        """사용자 생성"""
        user = User(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()
```

---

## API 응답 형식

### 성공 응답
모든 성공 응답은 일관된 형식을 따릅니다:

```json
{
  "success": true,
  "message": "요청이 성공했습니다",
  "data": {
    "id": 1,
    "name": "John Doe"
  }
}
```

### 에러 응답
모든 에러 응답도 일관된 형식을 따릅니다:

```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "message": "검증 실패",
  "details": {
    "field": "email",
    "reason": "이메일 형식이 유효하지 않습니다"
  }
}
```

---

## 에러 핸들링

### 커스텀 예외 사용

```python
from app.core.exceptions import (
    ValidationException,
    NotFound,
    DuplicateException,
)

# 검증 에러
raise ValidationException(
    message="이메일 형식이 유효하지 않습니다",
    details={"field": "email"},
)

# 리소스 없음
raise NotFound("사용자를 찾을 수 없습니다")

# 중복 에러
raise DuplicateException("이미 등록된 이메일입니다")
```

### 예외 계층 구조

```
AppException (기본)
├── ValidationException (400)
├── UnauthorizedException (401)
├── ForbiddenException (403)
├── NotFound (404)
└── DuplicateException (409)
```

---

## 테스트 작성

### 단위 테스트 (Unit Tests)

```python
import pytest
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_create_user_success(user_service):
    """사용자 생성 성공 테스트"""
    request = UserCreateRequest(
        email="test@example.com",
        password="password123",
    )
    user = await user_service.create_user(request)

    assert user.id is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_create_user_duplicate_email(user_service):
    """중복 이메일 에러 테스트"""
    request = UserCreateRequest(
        email="existing@example.com",
        password="password123",
    )

    with pytest.raises(DuplicateException):
        await user_service.create_user(request)
```

### 통합 테스트 (Integration Tests)

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user_endpoint(client: AsyncClient):
    """사용자 생성 엔드포인트 테스트"""
    response = await client.post(
        "/users",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["data"]["email"] == "test@example.com"
```

### 테스트 실행

```bash
# 전체 테스트
pytest

# 특정 파일만
pytest tests/integration/test_user.py

# 커버리지 포함
pytest --cov=app

# 마커별 실행
pytest -m unit
pytest -m integration
```

---

## 데이터베이스

### 트랜잭션 처리

Repository에서 자동으로 처리됩니다:

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 마이그레이션

```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "사용자 테이블 추가"

# 마이그레이션 적용
alembic upgrade head

# 이전 버전으로 롤백
alembic downgrade -1
```

---

## 환경 설정

### 하드코딩 금지
모든 설정값은 환경 변수 또는 config.py에서 관리합니다:

```python
# ❌ 잘못된 예
DATABASE_URL = "postgresql://user:password@localhost:5432/db"

# ✅ 올바른 예
from app.core.config import settings
DATABASE_URL = settings.DATABASE_URL
```

---

## 의존성 주입

FastAPI의 Depends를 사용합니다:

```python
from fastapi import Depends
from app.services.user_service import UserService


async def get_user_service(
    repository: UserRepository = Depends(),
) -> UserService:
    """UserService 의존성"""
    return UserService(repository)


@app.post("/users")
async def create_user(
    request: UserCreateRequest,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(request)
```

---

## 체크리스트

새 기능을 추가할 때 확인하세요:

- [ ] 3계층 구조 (Controller → Service → Repository)
- [ ] DTO 패턴 사용
- [ ] 예외 처리 (커스텀 예외)
- [ ] 응답 형식 일관성
- [ ] 함수/메서드 20줄 이상 시 분리
- [ ] 단위/통합 테스트 작성
- [ ] 환경 변수 사용 (하드코딩 금지)
- [ ] 주석은 비즈니스 로직에만
- [ ] pre-commit 통과

---

## 참고 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [Pytest 공식 문서](https://docs.pytest.org/)

# FastAPI Starter Kit

프로덕션 레벨의 FastAPI 백엔드 API 스타터 킷입니다. Python 3.12 LTS, PM2, Docker를 포함합니다.

## 📋 목차

- [기술 스택](#기술-스택)
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [개발 가이드](#개발-가이드)
- [배포](#배포)
- [테스트](#테스트)

---

## 🛠 기술 스택

### 코어
- **Python** 3.12 LTS (지원: 2028년 10월까지)
- **FastAPI** 0.104+ - 고성능 웹 프레임워크
- **Pydantic** V2 - 데이터 검증 & DTO
- **SQLAlchemy** 2.x - ORM
- **PostgreSQL** - 프로덕션 데이터베이스

### 개발/테스트
- **Pytest** + pytest-asyncio - 테스트 프레임워크
- **Black** - 코드 포매팅
- **Ruff** - 린팅
- **mypy** - 타입 체킹
- **pre-commit** - 깃 훅

### 프로세스 관리 & 인프라
- **PM2** - 프로세스 매니저
- **Docker** + Docker Compose - 컨테이너화
- **Nginx** - 리버스 프록시
- **Redis** - 캐싱

### 추가 기능
- **JWT** - 인증 토큰
- **Celery** - 비동기 작업 큐
- **structlog** - 구조화된 로깅
- **slowapi** - Rate Limiting

---

## 🚀 빠른 시작

### 사전 요구사항
- Python 3.12+
- PostgreSQL 12+
- Redis 6+
- Node.js (PM2 실행)
- Docker & Docker Compose (선택사항)

### 설치 및 실행

**1. 저장소 클론**
```bash
cd fastapi-starter
```

**2. 환경 설정**
```bash
cp .env.example .env
# .env 파일 편집하여 데이터베이스 설정 수정
```

**3. 의존성 설치**
```bash
# Poetry 사용
poetry install

# 또는 pip 사용
pip install -r requirements.txt
```

**4. 데이터베이스 마이그레이션**
```bash
alembic upgrade head
```

**5. 개발 서버 실행**

**방법 1: 직접 실행**
```bash
uvicorn app.main:app --reload --port 8000
```

**방법 2: PM2 사용**
```bash
npm install -g pm2
pm2 start ecosystem.config.js
```

**방법 3: Docker Compose 사용**
```bash
docker-compose up -d
```

### API 문서 접속
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json

---

## 📁 프로젝트 구조

```
fastapi-starter/
├── app/
│   ├── core/                  # 핵심 설정
│   │   ├── config.py         # 환경 설정
│   │   ├── database.py       # DB 연결
│   │   ├── logging.py        # 로깅 설정
│   │   └── exceptions.py     # 커스텀 예외
│   │
│   ├── models/               # SQLAlchemy ORM 모델
│   │   ├── base.py          # 기본 모델
│   │   └── ...
│   │
│   ├── schemas/              # Pydantic DTO
│   │   ├── response.py      # 응답 형식
│   │   └── ...
│   │
│   ├── controllers/          # API 라우트
│   │   ├── health.py        # 헬스 체크
│   │   └── ...
│   │
│   ├── services/             # 비즈니스 로직
│   │   └── ...
│   │
│   ├── repositories/         # DB 접근 계층
│   │   └── ...
│   │
│   ├── middlewares/          # 미들웨어
│   │   └── error_handler.py
│   │
│   ├── utils/                # 유틸리티
│   │   └── ...
│   │
│   └── main.py              # 애플리케이션 진입점
│
├── tests/                    # 테스트
│   ├── unit/                # 단위 테스트
│   ├── integration/         # 통합 테스트
│   └── conftest.py         # 테스트 설정
│
├── migrations/               # Alembic 마이그레이션
│
├── docker-compose.yml        # Docker Compose 설정
├── Dockerfile               # Docker 이미지 빌드
├── ecosystem.config.js       # PM2 설정
├── pyproject.toml           # Poetry 설정
├── pytest.ini               # Pytest 설정
├── .env.example             # 환경 변수 예시
├── CODING_GUIDE.md          # 코드 작성 가이드
└── README.md                # 이 파일
```

### 아키텍처
레이어드 아키텍처를 따릅니다:

```
Controller (라우트) → Service (비즈니스 로직) → Repository (데이터 접근)
```

자세한 내용은 [CODING_GUIDE.md](./CODING_GUIDE.md)를 참조하세요.

---

## 📚 개발 가이드

### 코드 스타일

**자동 포매팅:**
```bash
# Black 포매팅
black app/ tests/

# Ruff 린팅
ruff check app/ tests/

# 모두 한 번에 (권장)
pre-commit run --all-files
```

**Pre-commit 설정:**
```bash
# 설치
pre-commit install

# 커밋 시 자동으로 실행됨
git commit -m "메시지"
```

### 새 기능 추가

**1. 데이터베이스 모델 생성** (`app/models/`)
```python
from app.models.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
```

**2. DTO 스키마 생성** (`app/schemas/`)
```python
from pydantic import BaseModel, EmailStr

class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
```

**3. Repository 생성** (`app/repositories/`)
```python
class UserRepository:
    async def create(self, data):
        # DB 작업
        pass
```

**4. Service 생성** (`app/services/`)
```python
class UserService:
    async def create_user(self, request):
        # 비즈니스 로직
        pass
```

**5. Controller 생성** (`app/controllers/`)
```python
@router.post("/users")
async def create_user(request, service):
    user = await service.create_user(request)
    return SuccessResponse(data=user)
```

자세한 가이드는 [CODING_GUIDE.md](./CODING_GUIDE.md)를 참조하세요.

---

## 🧪 테스트

### 단위 테스트

```bash
# 모든 단위 테스트 실행
pytest tests/unit/

# 특정 테스트 파일
pytest tests/unit/test_user_service.py

# 특정 테스트 함수
pytest tests/unit/test_user_service.py::test_create_user
```

### 통합 테스트

```bash
# 모든 통합 테스트
pytest tests/integration/

# 헬스 체크 테스트
pytest tests/integration/test_health.py
```

### 전체 테스트 & 커버리지

```bash
# 전체 테스트 실행
pytest

# 커버리지 리포트 생성
pytest --cov=app --cov-report=html

# HTML 리포트 보기
open htmlcov/index.html
```

### 테스트 작성 예시

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    """사용자 생성 성공 테스트"""
    response = await client.post(
        "/users",
        json={
            "email": "test@example.com",
            "name": "Test User",
        }
    )

    assert response.status_code == 201
    assert response.json()["success"] is True
```

---

## 🐳 Docker를 사용한 배포

### 개발 환경

```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f api

# 서비스 중지
docker-compose down
```

### 프로덕션 배포

**1. 환경 설정**
```bash
cp .env.example .env.production
# .env.production 편집
```

**2. Docker 이미지 빌드**
```bash
docker build -t fastapi-starter:1.0.0 .
```

**3. 이미지 푸시** (선택사항)
```bash
docker tag fastapi-starter:1.0.0 your-registry/fastapi-starter:1.0.0
docker push your-registry/fastapi-starter:1.0.0
```

**4. 배포**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔒 보안

### 환경 변수
민감한 정보는 반드시 환경 변수로 관리하세요:
- 데이터베이스 URL
- API 키
- JWT 시크릿 키

```bash
# .env 파일 (버전 관리에서 제외)
SECRET_KEY=your-secret-key-here
```

### 프로덕션 체크리스트
- [ ] `DEBUG=False` 설정
- [ ] `SECRET_KEY` 변경
- [ ] HTTPS 활성화
- [ ] CORS 설정 확인
- [ ] 데이터베이스 백업 설정
- [ ] 로깅 및 모니터링 설정
- [ ] Rate Limiting 활성화

---

## 📊 모니터링

### 헬스 체크
```bash
curl http://localhost:8000/health
```

응답:
```json
{
  "success": true,
  "message": "애플리케이션이 정상 작동 중입니다",
  "data": {
    "status": "healthy"
  }
}
```

### PM2 모니터링
```bash
# PM2 프로세스 상태 확인
pm2 status

# 실시간 모니터링
pm2 monit

# 로그 확인
pm2 logs fastapi-api

# 재시작
pm2 restart fastapi-api

# 중지
pm2 stop fastapi-api
```

---

## 🔄 데이터베이스 마이그레이션

### 마이그레이션 생성
```bash
alembic revision --autogenerate -m "사용자 테이블 추가"
```

### 마이그레이션 적용
```bash
# 최신 버전으로 업그레이드
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade 1234abc
```

### 마이그레이션 롤백
```bash
# 이전 버전으로
alembic downgrade -1

# 모든 마이그레이션 제거
alembic downgrade base
```

---

## 📦 의존성 관리

### Poetry 사용 (권장)
```bash
# 의존성 추가
poetry add package-name

# 의존성 제거
poetry remove package-name

# 의존성 업데이트
poetry update

# requirements.txt 생성
poetry export -f requirements.txt --output requirements.txt
```

### pip 사용
```bash
# 의존성 설치
pip install -r requirements.txt

# requirements.txt 생성
pip freeze > requirements.txt
```

---

## 🐛 문제 해결

### PostgreSQL 연결 오류
```bash
# 데이터베이스 상태 확인
docker-compose ps

# 데이터베이스 재시작
docker-compose restart db

# 로그 확인
docker-compose logs db
```

### 마이그레이션 충돌
```bash
# 마이그레이션 히스토리 확인
alembic history

# 충돌하는 마이그레이션 제거 후 다시 생성
alembic downgrade -1
alembic revision --autogenerate -m "새 마이그레이션"
```

### 테스트 실패
```bash
# 테스트 데이터베이스 초기화
pytest --cache-clear

# 자세한 로그 보기
pytest -vv -s tests/
```

---

## 📚 참고 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [Pytest 공식 문서](https://docs.pytest.org/)
- [Docker 공식 문서](https://docs.docker.com/)
- [PM2 공식 문서](https://pm2.keymetrics.io/)

---

## 📝 코드 작성 가이드

[CODING_GUIDE.md](./CODING_GUIDE.md)를 참조하세요. 아래 주요 사항들을 포함합니다:

- 레이어드 아키텍처 적용
- DTO 패턴 사용
- 의존성 주입
- 에러 핸들링
- API 응답 형식 일관성
- 테스트 작성 가이드
- 환경 변수 관리

---

## 🤝 기여

1. Feature Branch 생성: `git checkout -b feature/새기능`
2. 코드 변경: `git add .`
3. Commit: `git commit -m "feature: 새기능 추가"`
4. Push: `git push origin feature/새기능`
5. Pull Request 생성

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

---

## 💬 질문 & 피드백

문제가 있거나 제안사항이 있으시면 이슈를 생성해주세요.

---

## 🎯 Checklist (새 프로젝트 시작)

- [ ] `.env` 파일 생성 및 설정
- [ ] `poetry install` 또는 `pip install -r requirements.txt`
- [ ] `alembic upgrade head` (DB 마이그레이션)
- [ ] `pre-commit install` (깃 훅 설정)
- [ ] `pytest` (테스트 실행)
- [ ] 헬스 체크 엔드포인트 확인
- [ ] API 문서 (http://localhost:8000/docs) 확인

---

**Happy Coding! 🚀**

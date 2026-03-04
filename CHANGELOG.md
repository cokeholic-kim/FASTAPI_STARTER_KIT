# Changelog

이 문서는 프로젝트의 주목할 만한 변경 사항을 기록합니다.

포맷은 [Keep a Changelog](https://keepachangelog.com/)를 따르며,
버전은 [시맨틱 버전](https://semver.org/) 기준으로 관리합니다.

## [Unreleased]

### Added
- 문서/운영성 보강: API 계약 문서, CI 뱃지, Changelog 정책 추가

### Changed
- `README.md`의 구현 상태와 테스트 검증 현황을 체크리스트로 정리
- `CHANGELOG.md`를 버전 기반 기록 형식으로 재정렬

### Fixed
- 중복 생성/동시성, 삭제 응답, 테스트 격리, 경고 정리 등 안정성 이슈 반영

### Security
- 요청/로그에서 민감정보 마스킹 정책 정합성 강화

## [0.2.0] - 2026-03-05

### Added
- 사용자 API(회원) CRUD 기능 정리
- 운영 관측성 강화
  - `/metrics`, `/observability/health`, `/observability/request-metadata`
  - 요청/메트릭 분리 수집 정책
- 배치 작업용 correlation context 샘플 적용
- 민감정보(이메일/토큰/패스워드) 마스킹 정책 적용

### Changed
- 예외 미들웨어와 응답 스키마 동작 정합성 정리
- 테스트 DB 세션 라이프사이클 정리 및 `override_get_db` 일관성 강화
- `on_event`를 `lifespan` 전환

### Fixed
- 중복 이메일 동시 생성 시 409 반환으로 일관화
- `DELETE /users/{id}`의 204 응답 본문 제거
- `datetime.utcnow`를 `datetime.now(timezone.utc)`로 교체

### Security
- 로깅/쿼리 마스킹에서 민감값 처리 강화

### Testing
- 단위 테스트: `tests/unit` (3 passed)
- 통합 테스트: `tests/integration` (8 passed)
- 전체 테스트: 13 passed
- CI는 `main`, `master` 브랜치에서 `push`, `pull_request` 트리거 실행

## [0.1.0] - 2026-03-05

### Added
- FastAPI 스타터 기본 골격 구성
- `/health` 및 사용자 CRUD 라우트 기본 구현
- GitHub Actions 기반 CI 초기 구성
- Alembic 마이그레이션 기본 구조

### Fixed
- 초기 예외 처리/응답 경로 정합성 보강
- 기본 테스트 인프라 구축

[Unreleased]: https://github.com/cokeholic-kim/FASTAPI_STARTER_KIT/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/cokeholic-kim/FASTAPI_STARTER_KIT/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/cokeholic-kim/FASTAPI_STARTER_KIT/releases/tag/v0.1.0

# db-reset

DB 초기화 (마이그레이션 + 시드 데이터)

```bash
echo "🔄 데이터베이스를 초기화합니다..."

# 1. 기존 서비스 중지 및 볼륨 삭제
echo "🛑 기존 데이터 제거 중..."
docker-compose down -v

# 2. PostgreSQL 및 Redis 시작
echo "📦 PostgreSQL과 Redis 시작 중..."
docker-compose up -d postgres redis

# 3. DB 준비 대기
echo "⏳ DB 준비 중... (3초 대기)"
sleep 3

# 4. 마이그레이션 실행
echo "🔄 Alembic 마이그레이션 실행 중..."
docker-compose exec -T api alembic upgrade head

echo "✅ 데이터베이스 초기화 완료!"
```

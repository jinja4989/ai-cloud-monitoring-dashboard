# 1. 베이스 이미지 (Python 3.10, 가벼운 Debian 기반)
FROM python:3.10-slim

# 2. 컨테이너 내부 작업 디렉토리
WORKDIR /app

# 3. 빌드에 필요한 시스템 패키지 설치
#    (psutil, cryptography 등 C 확장 대비)
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
 && rm -rf /var/lib/apt/lists/*

# 4. requirements.txt 먼저 복사 (Docker 캐시 최적화)
COPY requirements.txt .

# 5. pip / setuptools / wheel 최신화 (빌드 오류 방지)
RUN pip install --upgrade pip setuptools wheel

# 6. Python 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 7. 나머지 소스 코드 복사
COPY . .

# 8. Flask 기본 포트
EXPOSE 5000

# 9. 애플리케이션 실행
CMD ["python", "app.py"]

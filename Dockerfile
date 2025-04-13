FROM python:3.12-slim

# 시스템 패키지 업데이트 및 필요한 패키지 설치 (libzbar0, build-essential, python3-dev 추가)
RUN apt-get update && \
    apt-get install -y libzbar0 build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements.txt 복사 및 의존성 설치 (캐시 무효화 옵션 사용)
COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY . .

# Gunicorn을 통해 앱 실행 (필요한 경우 CMD 변경)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]

FROM python:3.12-slim

# 시스템 패키지 업데이트 및 libzbar0, build-essential, python3-dev 설치
RUN apt-get update && \
    apt-get install -y libzbar0 build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# requirements.txt 복사
COPY requirements.txt .

# pip 업데이트 후 의존성 설치 (캐시 무효화 옵션 추가)
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# Gunicorn으로 앱 실행, Railway에서는 8080 포트를 사용 (CMD는 상황에 따라 조정)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]

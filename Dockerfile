FROM python:3.12-slim

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y libzbar0 build-essential python3-dev python3-distutils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# pip를 최신 버전으로 업그레이드 후, requirements.txt를 이용하여 의존성을 설치 (캐시 무효화 옵션 사용)
RUN pip install --upgrade pip --no-cache-dir && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]

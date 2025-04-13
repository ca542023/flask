# Python 3.12-slim 베이스 이미지 사용
FROM python:3.12-slim

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && \
    apt-get install -y \
      libzbar0 \
      libzbar-dev \
      build-essential \
      python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 파일 복사
COPY requirements.txt .

# pip 최신 버전으로 업데이트 후 requirements.txt에 있는 패키지 설치
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 앱 소스코드 복사
COPY . .

# Gunicorn으로 애플리케이션 실행
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]

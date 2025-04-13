# Python 3.12-slim 베이스 이미지 사용
FROM python:3.12-slim

# 시스템 패키지 업데이트 및 libzbar0 설치
RUN apt-get update && \
    apt-get install -y libzbar0 && \
    rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# Gunicorn을 통해 앱 실행 (Railway에서 외부 포트는 8080 사용)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]

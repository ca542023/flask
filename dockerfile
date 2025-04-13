# 베이스 이미지 선택 (Railway에서 사용한 Nixpacks 이미지를 대신 사용하거나, Python 기반 이미지를 사용)
FROM python:3.12-slim

# 시스템 패키지 업데이트 및 libzbar0 설치
RUN apt-get update && apt-get install -y libzbar0

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# Gunicorn을 통해 앱 실행 (Procfile 대신 가능)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]

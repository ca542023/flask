FROM python:3.12-slim

# 시스템 패키지 업데이트 및 필요한 패키지 설치 (libzbar0, build-essential, python3-dev, python3-distutils)
RUN apt-get update && \
    apt-get install -y libzbar0 build-essential python3-dev python3-distutils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 파일 복사
COPY requirements.txt .

# pip와 setuptools 업그레이드 후, requirements.txt에 있는 패키지 설치
RUN pip install --upgrade pip setuptools --no-cache-dir && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# Gunicorn으로 앱 실행 (Railway는 포트 8080 사용)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]

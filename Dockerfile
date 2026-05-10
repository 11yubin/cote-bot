FROM python:3.12-slim

WORKDIR /app

# 의존성 레이어를 코드와 분리해 캐시 효율 높임
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# data 디렉토리는 볼륨으로 마운트되므로 런타임에 생성됨
RUN mkdir -p data

CMD ["python", "main.py"]

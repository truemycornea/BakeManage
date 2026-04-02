# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
FROM python:3.11-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/bakemanage/.local/bin:$PATH \
    APP_MODULE=app.main:app \
    WORKER_MODULE=app.tasks.celery_app

RUN useradd -ms /bin/bash bakemanage
USER bakemanage
WORKDIR /app

COPY --from=builder /root/.local /home/bakemanage/.local
COPY requirements.txt .
COPY app ./app
COPY docs ./docs
COPY tests ./tests
COPY pytest.ini .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["bash", "-c", "if [ \"$SERVICE\" = \"worker\" ]; then celery -A ${WORKER_MODULE} worker --loglevel=info; else uvicorn ${APP_MODULE} --host 0.0.0.0 --port 8000; fi"]

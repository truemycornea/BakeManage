# BakeManage IP Assignment: All contributions assign IP to BakeManage (c) 2026
# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="BakeManage Platform API" \
      org.opencontainers.image.description="Enterprise-grade ERP for Indian bakeries" \
      org.opencontainers.image.source="https://github.com/truemycornea/BakeManage" \
      org.opencontainers.image.licenses="Proprietary"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/bakemanage/.local/bin:$PATH \
    APP_MODULE=app.main:app \
    WORKER_MODULE=app.tasks.celery_app

RUN useradd -ms /bin/bash bakemanage
USER bakemanage
WORKDIR /app

COPY --from=builder --chown=bakemanage:bakemanage /root/.local /home/bakemanage/.local
COPY --chown=bakemanage:bakemanage requirements.txt .
COPY --chown=bakemanage:bakemanage app ./app
COPY --chown=bakemanage:bakemanage docs ./docs
COPY --chown=bakemanage:bakemanage tests ./tests
COPY --chown=bakemanage:bakemanage pytest.ini .

ENV PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

CMD ["bash", "-c", "if [ \"$SERVICE\" = \"worker\" ]; then celery -A ${WORKER_MODULE} worker --loglevel=info; else uvicorn ${APP_MODULE} --host 0.0.0.0 --port 8000; fi"]

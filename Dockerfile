FROM python:3.12-slim AS base

WORKDIR /srv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


FROM base AS test

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt


FROM base AS runtime

RUN useradd --create-home --uid 1000 appuser && \
    chown -R appuser:appuser /srv

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

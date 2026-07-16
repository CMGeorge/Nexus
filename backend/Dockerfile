# ── Build stage: uv + dependencies ──
FROM ghcr.io/astral-sh/uv:latest AS uv

# ── Runtime stage ──
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Copy uv binary from uv image
COPY --from=uv /uv /usr/local/bin/uv

# Install dependencies (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --python-preference only-system

# Copy application code
COPY alembic.ini ./
COPY alembic/ alembic/
COPY app/ app/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

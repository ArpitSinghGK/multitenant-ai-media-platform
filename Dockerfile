FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -e .

EXPOSE 8080

# Default: the API (Control Plane). Override the command for the Celery worker.
CMD ["uvicorn", "aiplatform.main:app", "--host", "0.0.0.0", "--port", "8080", "--app-dir", "src"]

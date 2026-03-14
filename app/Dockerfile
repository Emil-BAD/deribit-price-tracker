FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

# Install dependencies from app/requirements.txt inside repo root.
RUN if [ -f /app/app/requirements.txt ]; then \
      pip install --no-cache-dir -r /app/app/requirements.txt; \
    fi

EXPOSE 8000

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Adjust python path if needed, though with /app as workdir and code in backend/
# we might need to be careful. The docker-compose mounts ./backend to /app/backend
# so here we probably want to COPY . . to get the whole structure or just backend.
# The user structure has `backend/` as the django project root essentially.
# Let's assume manage.py is in backend/manage.py based on previous `list_dir`.
# So we switch WORKDIR to /app/backend to run manage.py easily.

WORKDIR /app/backend

CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT

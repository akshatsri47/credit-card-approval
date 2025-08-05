# Dockerfile

FROM python:3.11-slim


RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-client \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy your project code
COPY . .

EXPOSE 8000

# 4) Wait for Postgres, migrate, then start Django dev server
CMD sh -c "\
    until pg_isready -h db -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\"; do sleep 1; done && \
    python manage.py migrate --noinput && \
    python manage.py runserver 0.0.0.0:8000 \
"

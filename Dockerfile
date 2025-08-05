# Use the official Python image
FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Expose Django’s port
EXPOSE 8000

# Default command: run migrations then dev server
CMD sh -c " \
    until pg_isready -h db -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\"; do sleep 1; done && \
    python manage.py migrate --noinput && \
    python manage.py runserver 0.0.0.0:8000 \
"

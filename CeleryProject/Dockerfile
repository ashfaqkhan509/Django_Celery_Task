# Base image
FROM python:3.10-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create non-root user and set ownership of /app
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose Django port
EXPOSE 8000

# Default command (use gunicorn for production)
# CMD ["gunicorn", "CeleryProject.wsgi:application", "--bind", "0.0.0.0:8000"]

# Default command (use Django's development server for learning)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


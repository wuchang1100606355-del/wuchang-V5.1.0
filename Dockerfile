# Wuchang Survival Node Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONUTF8=1

# Set work directory
WORKDIR /app

# Install dependencies
# (Combining commands to reduce layers)
RUN pip install --no-cache-dir \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib \
    schedule \
    watchdog \
    requests

# Copy project files
COPY . /app/

# Default command (overridden in docker-compose)
CMD ["python", "wuchang_tools_library/core_sister_service.py"]

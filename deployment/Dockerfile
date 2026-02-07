FROM python:3.9-slim

WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies for ALL Inventions
# - Flask/Ngrok: Web Endpoint
# - Google: Workspace/Drive API
# - Odoo: XMLRPC (stdlib)
# - Kasa: TP-Link Devices (presumed invention)
# - LLM Support: LangChain, Ollama, OpenAI (for compatibility)
RUN pip install --no-cache-dir feedparser apscheduler \
    flask \
    requests \
    pyngrok \
    google-auth \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client \
    python-kasa \
    psutil \
    langchain \
    langchain-community \
    langchain-ollama \
    ollama

# Environment Variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/wuchang_space

# Copy application code
COPY voice_service/ /app/
COPY voice_service/templates/ /app/templates/

EXPOSE 5000

# Meimei: The System Operator
CMD ["python", "web_commander.py"]


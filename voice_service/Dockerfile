FROM python:3.9-slim

# Install system dependencies for PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
RUN pip install --no-cache-dir speechrecognition pyttsx3 requests pyaudio

COPY . .

# Default to text mode if no mic device passed, but intent is voice
CMD ["python", "voice_commander.py"]

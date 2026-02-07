import os
import sys

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
except Exception as e:
    print("Please install google-cloud-aiplatform: pip install google-cloud-aiplatform")
    sys.exit(1)

PROJECT_ID = os.environ.get("PROJECT_ID") or "coffee-spark-ai-barista-b10b5"
LOCATION = os.environ.get("LOCATION") or "us-central1"
MODEL = os.environ.get("MODEL") or "gemini-1.0-pro"

print("ADC file:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(MODEL)
    resp = model.generate_content("Say hi as Little J in 5 words.")
    print("OK:", resp.text)
except Exception as e:
    print("ERROR:", e)
    sys.exit(2)

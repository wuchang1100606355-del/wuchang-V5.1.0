from flask import Flask, jsonify, send_from_directory, request
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Base directory for static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')

# Configuration (Ideally from env vars)
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT', 'coffee-spark-ai-barista-b10b5')
LOCATION = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')

def init_vertex_ai():
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        return GenerativeModel
    except Exception as e:
        logger.error(f"Vertex AI init failed: {e}")
        return None

@app.route('/')
def index():
    return "Wuchang Spatial 3D System API v1.0"

@app.route('/earth-3d-viewer')
def viewer():
    """Serve the 3D Viewer HTML"""
    return send_from_directory(FRONTEND_DIR, 'earth_3d_viewer.html')

@app.route('/property-report')
def report():
    return send_from_directory(FRONTEND_DIR, 'property_report.html')

@app.route('/api/spatial/stats')
def stats():
    """Return mock spatial statistics"""
    return jsonify({
        "villages": ["五常里", "五順里", "仁忠里"],
        "total_area_km2": 1.2,
        "buildings_count": 856,
        "status": "active"
    })

@app.route('/api/spatial/analyze', methods=['POST'])
def analyze_property():
    """
    Analyze a property inspection point using Vertex AI.
    Accepts JSON: {"prompt": "...", "image_data": "..." (optional)}
    """
    data = request.json or {}
    prompt = data.get('prompt', 'Analyze this property location for maintenance issues.')
    
    # Check if we can use Vertex AI
    GenModel = init_vertex_ai()
    
    if GenModel:
        try:
            model = GenModel("gemini-1.5-pro-preview-0409")
            # In a real scenario, we would decode base64 image_data here
            # For now, we simulate text-based analysis or handle the prompt
            responses = model.generate_content(prompt)
            return jsonify({
                "source": "Vertex AI",
                "analysis": responses.text
            })
        except Exception as e:
            logger.error(f"Vertex AI generation failed: {e}")
            return jsonify({
                "source": "Fallback (Error)",
                "analysis": f"AI 分析服務暫時無法使用: {str(e)}。請稍後再試。"
            })
    else:
        # Fallback Mock Response if Vertex AI is not configured/auth missing
        return jsonify({
            "source": "Simulation (No Auth)",
            "analysis": "模擬分析：檢測到該區域（五常公園）設施有輕微鏽蝕，建議安排除鏽保養。人流密度適中，無立即安全隱患。"
        })


if __name__ == '__main__':
    # Listen on all interfaces, port 8080
    app.run(host='0.0.0.0', port=8080)

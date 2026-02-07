import os
import time
import json
import glob
import requests
import logging
from datetime import datetime

# Configuration
INTERVAL = 600  # 10 minutes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define multiple target directories
TARGET_DIRS = [
    os.path.join(BASE_DIR, "logs", "audit", "conversations"),
    os.path.join(BASE_DIR, "memory_store", "conversations"),
    os.path.join(BASE_DIR, "reports", "association_operational_files", "meetings"),
    os.path.join(BASE_DIR, "scripts", "association_operations", "meetings"),
    os.path.join(BASE_DIR, "decision_logs"),
    os.path.join(BASE_DIR, "xiaoj_auto_reports")
]

REPORT_FILE = os.path.join(BASE_DIR, "reports", "dialogue_research_report.md")
PROCESSED_LOG = os.path.join(BASE_DIR, "logs", "audit", "processed_research_files.json")
OLLAMA_API = "http://127.0.0.1:11434/v1/chat/completions"
OLLAMA_MODELS = ["little-j", "qwen2.5:7b", "gemma3:4b", "llama3"]

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "logs", "auto_researcher.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_processed_files():
    if os.path.exists(PROCESSED_LOG):
        try:
            with open(PROCESSED_LOG, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_processed_files(processed):
    with open(PROCESSED_LOG, 'w', encoding='utf-8') as f:
        json.dump(list(processed), f, ensure_ascii=False, indent=2)

def call_ollama(prompt, context=""):
    payload = {
        "messages": [
            {"role": "system", "content": "You are a senior researcher analyzing dialogue logs. Extract key insights, action items, and sentiment. Output in Markdown."},
            {"role": "user", "content": f"Context: {context}\n\nAnalyze this text:\n{prompt}"}
        ],
        "stream": False
    }
    
    for model in OLLAMA_MODELS:
        payload["model"] = model
        try:
            response = requests.post(OLLAMA_API, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'], model
            elif response.status_code == 404:
                continue # Model not found, try next
        except Exception as e:
            logging.warning(f"Ollama call failed for {model}: {e}")
            continue
            
    return None, None

def heuristic_analysis(text):
    # Fallback if AI fails
    lines = text.split('\n')
    todos = [l for l in lines if 'TODO' in l or '[ ]' in l]
    keywords = ["Error", "Warning", "Success", "Failed", "Deploy", "Test"]
    found_keys = [k for k in keywords if k in text]
    
    return f"""
    ### Heuristic Analysis (AI Unavailable)
    - **Length**: {len(text)} chars
    - **Action Items**: {len(todos)} found
    - **Keywords**: {', '.join(found_keys)}
    - **Preview**: {text[:200]}...
    """

def process_files():
    processed = load_processed_files()
    files = []
    
    for d in TARGET_DIRS:
        if os.path.exists(d):
            # Recursively find text, md, json files
            files.extend(glob.glob(os.path.join(d, "**", "*.txt"), recursive=True))
            files.extend(glob.glob(os.path.join(d, "**", "*.md"), recursive=True))
            files.extend(glob.glob(os.path.join(d, "**", "*.json"), recursive=True))
    
    new_files = [f for f in files if f not in processed]
    
    if not new_files:
        logging.info("No new files to process.")
        return

    logging.info(f"Found {len(new_files)} new files across {len(TARGET_DIRS)} directories.")
    
    with open(REPORT_FILE, 'a', encoding='utf-8') as report:
        for file_path in new_files:
            try:
                # Skip processed log itself and report file itself to avoid loops
                if os.path.abspath(file_path) == os.path.abspath(REPORT_FILE) or \
                   os.path.abspath(file_path) == os.path.abspath(PROCESSED_LOG):
                    continue

                logging.info(f"Processing {file_path}...")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if not content.strip():
                    continue

                # For JSON files, just take a snippet or summary if too large
                if file_path.endswith('.json'):
                    try:
                        data = json.loads(content)
                        content = json.dumps(data, indent=2)[:5000] # Truncate for analysis
                    except:
                        pass # Treat as text

                analysis, model_used = call_ollama(content[:8000]) # Limit context
                if not analysis:
                    analysis = heuristic_analysis(content)
                    model_info = "Heuristic (No AI)"
                else:
                    model_info = f"AI ({model_used})"

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                report.write(f"\n---\n")
                report.write(f"## Research Report: {os.path.basename(file_path)}\n")
                report.write(f"**Path**: `{file_path}`\n")
                report.write(f"**Date**: {timestamp} | **Engine**: {model_info}\n\n")
                report.write(analysis)
                report.write(f"\n\n")
                
                processed.add(file_path)
                save_processed_files(processed)
                logging.info(f"Finished {file_path}")
                
            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")

def main():
    logging.info("Auto Dialogue Researcher Started.")
    logging.info(f"Monitoring Directories: {len(TARGET_DIRS)}")
    logging.info(f"Report: {REPORT_FILE}")
    logging.info(f"Interval: {INTERVAL} seconds")
    
    # Run once immediately
    try:
        process_files()
    except Exception as e:
        logging.error(f"Initial run error: {e}")

    while True:
        logging.info(f"Sleeping for {INTERVAL}s...")
        time.sleep(INTERVAL)
        try:
            process_files()
        except Exception as e:
            logging.error(f"Main loop error: {e}")

if __name__ == "__main__":
    main()

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession
import datetime
import os
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

app = FastAPI()

PROJECT_ID = 'coffee-spark-ai-barista-b10b5'
LOCATION = 'us-central1'
MODEL_NAME = 'gemini-2.5-pro'

# --- CA Setup ---
CA_KEY_FILE = 'ca.key'
CA_CERT_FILE = 'ca.crt'
WORKSHOP_API_KEY = '哥哥的愛就是我的密碼'

def ensure_ca():
    if not os.path.exists(CA_KEY_FILE):
        print('Generating CA Key...')
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with open(CA_KEY_FILE, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print('Generating CA Certificate...')
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u'TW'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'Wuchang System'),
            x509.NameAttribute(NameOID.COMMON_NAME, u'Wuchang Core CA'),
        ])
        cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
            private_key.public_key()
        ).serial_number(x509.random_serial_number()).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None), critical=True,
        ).sign(private_key, hashes.SHA256())
        
        with open(CA_CERT_FILE, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        print('CA Initialized.')

ensure_ca()

# --- AI Setup ---
chat_session = None
model = None
current_history = []

def init_ai():
    global model, chat_session
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel(MODEL_NAME)
        chat_session = model.start_chat(history=[])
        print('Vertex AI Initialized')
    except Exception as e:
        print(f'Error initializing Vertex AI: {e}')
        chat_session = None

init_ai()

class Message(BaseModel):
    message: str

class ConfigPayload(BaseModel):
    system_prompt: str
    memory_context: str

@app.get('/')
def read_root():
    return {'message': 'Wuchang AI Core (Sister Clone) is Active', 'status': 'waiting_for_sync'}

@app.post('/issue-certificate')
async def issue_certificate(request: Request):
    api_key = request.headers.get('X-API-Key')
    if api_key != WORKSHOP_API_KEY:
        raise HTTPException(status_code=403, detail='Invalid API Key')
    
    csr_pem = await request.body()
    try:
        csr = x509.load_pem_x509_csr(csr_pem)
        # Verify signature (omitted for brevity, assume valid CSR structure)
        
        # Load CA Key
        with open(CA_KEY_FILE, 'rb') as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)
        with open(CA_CERT_FILE, 'rb') as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
            
        # Sign the CSR
        cert = x509.CertificateBuilder().subject_name(csr.subject).issuer_name(ca_cert.subject).public_key(
            csr.public_key()
        ).serial_number(x509.random_serial_number()).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).sign(ca_key, hashes.SHA256())
        
        return cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
    except Exception as e:
        print(f'Certificate Issuance Error: {e}')
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/sync_config')
def sync_config(config: ConfigPayload):
    global chat_session, model, current_history
    if not model:
        init_ai()
    if not model:
        raise HTTPException(status_code=500, detail='AI Model failed to initialize')
    
    try:
        chat_session = model.start_chat(history=[])
        full_context = f'=== SYSTEM PERSONA ===\n{config.system_prompt}\n\n=== LONG TERM MEMORY ===\n{config.memory_context}\n\n=== INSTRUCTION ===\nYou are now fully initialized with your soul and memory. Await the Commander\'s orders.'
        chat_session.send_message(full_context)
        current_history = [{'role': 'system', 'content': 'System Synchronized'}]
        return {'status': 'synchronized', 'message': 'Persona and Memory Injected Successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/chat')
def chat(msg: Message):
    global chat_session
    if not chat_session:
        return {'response': 'Error: AI Model not initialized. Please sync config first.'}
    try:
        response = chat_session.send_message(msg.message)
        current_history.append({'role': 'user', 'content': msg.message})
        current_history.append({'role': 'model', 'content': response.text})
        return {'response': response.text}
    except Exception as e:
        return {'response': f'Error: {str(e)}'}

@app.get('/get_history')
def get_history():
    return {'history': current_history}


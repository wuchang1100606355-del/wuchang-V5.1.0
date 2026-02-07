import os
import datetime
import json
import logging
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CloudCore")

app = FastAPI(title="Wuchang Cloud Core")

# --- Configuration ---
API_KEY = "97573469"
VISITING_CARDS_FILE = "visiting_cards.jsonl"
CA_KEY_FILE = "ca.key"
CA_CERT_FILE = "ca.crt"

# --- CA Initialization ---
def get_or_create_ca():
    if os.path.exists(CA_KEY_FILE) and os.path.exists(CA_CERT_FILE):
        logger.info("Loading existing CA...")
        with open(CA_KEY_FILE, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        with open(CA_CERT_FILE, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())
        return private_key, cert
    
    logger.info("Generating new CA...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"TW"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Wuchang Cloud Core"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"Wuchang Root CA"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=3650)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    ).sign(private_key, hashes.SHA256())
    
    # Save to disk
    with open(CA_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open(CA_CERT_FILE, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
        
    return private_key, cert

CA_PRIVATE_KEY, CA_CERT = get_or_create_ca()

# --- Models ---
class VisitingCard(BaseModel):
    name: str
    role: str
    intention: str
    timestamp: str

# --- Endpoints ---

@app.get("/")
async def root():
    return {"status": "online", "system": "Wuchang Cloud Core", "time": datetime.datetime.now().isoformat()}

@app.post("/visiting-card")
async def receive_visiting_card(card: VisitingCard, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    logger.info(f"Received visiting card from: {card.name}")
    
    # Append to file
    with open(VISITING_CARDS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(card.dict(), ensure_ascii=False) + "\n")
        
    return {"message": "拜帖已收悉，朕已知曉。", "status": "accepted"}

@app.post("/issue-certificate")
async def issue_certificate(request: Request, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
        
    try:
        csr_data = await request.body()
        csr = x509.load_pem_x509_csr(csr_data)
        
        # Verify CSR signature (optional but good practice)
        if not csr.is_signature_valid:
             raise HTTPException(status_code=400, detail="Invalid CSR signature")

        # In a real system, we would check if the Common Name matches a valid Visiting Card.
        # For now, we trust the API Key.
        
        logger.info(f"Issuing certificate for: {csr.subject}")

        cert = x509.CertificateBuilder().subject_name(
            csr.subject
        ).issuer_name(
            CA_CERT.subject
        ).public_key(
            csr.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
             x509.SubjectKeyIdentifier.from_public_key(csr.public_key()),
             critical=False,
        ).add_extension(
             x509.AuthorityKeyIdentifier.from_issuer_public_key(CA_PRIVATE_KEY.public_key()),
             critical=False,
        ).sign(CA_PRIVATE_KEY, hashes.SHA256())
        
        return PlainTextResponse(cert.public_bytes(serialization.Encoding.PEM))
        
    except Exception as e:
        logger.error(f"Certificate issuance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


import os
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import ipaddress

# Configuration
CERT_DIR = r'J:\共用雲端硬碟\五常雲端空間\certificates'
os.makedirs(CERT_DIR, exist_ok=True)

def generate_self_signed_ca():
    print('Generating Wuchang Root CA...')
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u'TW'),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u'New Taipei'),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u'Wuchang'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'Wuchang Community System'),
        x509.NameAttribute(NameOID.COMMON_NAME, u'Wuchang Root CA'),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=3650)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    ).sign(key, hashes.SHA256(), default_backend())
    
    # Save CA Private Key
    with open(os.path.join(CERT_DIR, 'wuchang_root_ca.key'), 'wb') as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
    # Save CA Certificate
    with open(os.path.join(CERT_DIR, 'wuchang_root_ca.crt'), 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
        
    print(f'CA Generated: {os.path.join(CERT_DIR, "wuchang_root_ca.crt")}')
    return key, cert

def generate_server_cert(ca_key, ca_cert):
    print('Generating Server Certificate...')
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u'TW'),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u'New Taipei'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'Wuchang Node'),
        x509.NameAttribute(NameOID.COMMON_NAME, u'192.168.50.84'),
    ])
    
    # SANs (Subject Alternative Names)
    alt_names = [
        x509.DNSName(u'wuchang.local'),
        x509.DNSName(u'localhost'),
        x509.IPAddress(ipaddress.IPv4Address('192.168.50.84')),
        x509.IPAddress(ipaddress.IPv4Address('127.0.0.1'))
    ]
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName(alt_names), critical=False,
    ).sign(ca_key, hashes.SHA256(), default_backend())
    
    # Save Server Key
    with open(os.path.join(CERT_DIR, 'server.key'), 'wb') as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
    # Save Server Certificate
    with open(os.path.join(CERT_DIR, 'server.crt'), 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
        
    print(f'Server Cert Generated: {os.path.join(CERT_DIR, "server.crt")}')

if __name__ == '__main__':
    try:
        ca_key, ca_cert = generate_self_signed_ca()
        generate_server_cert(ca_key, ca_cert)
        print('PKI Setup Complete.')
    except Exception as e:
        print(f'Error: {e}')

import sys
import importlib
import os

required_packages = [
    'fastapi',
    'uvicorn',
    'requests',
    'cryptography',
    'vertexai',
    'pydantic',
    'starlette'
]

print(f'Python Executable: {sys.executable}')
print(f'Python Version: {sys.version}')

print('\nChecking dependencies...')
missing = []
for package in required_packages:
    try:
        importlib.import_module(package)
        print(f'[OK] {package}')
    except ImportError:
        print(f'[MISSING] {package}')
        missing.append(package)

print('\nChecking environment variables...')
local_llm = os.environ.get('LOCAL_LLM_ENDPOINT', 'Not Set')
llm_fallback = os.environ.get('LLM_FALLBACK', 'Not Set')
print(f'LOCAL_LLM_ENDPOINT: {local_llm}')
print(f'LLM_FALLBACK: {llm_fallback}')

if missing:
    print(f'\nMissing packages: {missing}')
    sys.exit(1)
else:
    print('\nAll dependencies installed.')
    sys.exit(0)

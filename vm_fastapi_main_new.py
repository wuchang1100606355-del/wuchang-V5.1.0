import os
import datetime
import json
import asyncio
from typing import Dict, List, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import subprocess
import re
import platform
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

app = FastAPI()

# CORS for local devices behind router
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Vertex AI Init
PROJECT_ID = 'coffee-spark-ai-barista-b10b5'
LOCATION = 'us-central1'
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel('gemini-2.5-pro')
    chat = model.start_chat()
except Exception as e:
    print(f"Vertex AI Init Warning: {e}")

# Local LLM endpoint config (primary)
# e.g., http://localhost:11434/v1/chat/completions
LOCAL_LLM_ENDPOINT = os.environ.get('LOCAL_LLM_ENDPOINT')
LOCAL_LLM_MODEL = os.environ.get('LOCAL_LLM_MODEL', 'gpt-neo')
# optional for OpenAI-compatible servers
LOCAL_LLM_API_KEY = os.environ.get('LOCAL_LLM_API_KEY')
LLM_FALLBACK = os.environ.get('LLM_FALLBACK', '1') == '1'  # 允許雲端備援（1=允許, 0=禁用）

# CA Settings
CA_KEY_FILE = 'ca.key'
CA_CERT_FILE = 'ca.crt'
WORKSHOP_API_KEY = "97573469"

# Simple in-memory device registry and command queues
devices: Dict[str, Dict[str, Any]] = {}
commands_by_type: Dict[str, List[Dict[str, Any]]] = {"POS": [], "CUSTOMER": []}
POS_UI_URL = os.environ.get('POS_UI_URL', 'http://localhost:8069/pos/ui')
CUSTOMER_UI_URL = os.environ.get(
    'CUSTOMER_UI_URL', 'http://localhost:8069/pos/customer_display')
EVENTS_LOG_FILE = 'events.log.jsonl'


# --- Simple Event Broker for live dashboard (SSE) ---
class EventBroker:
    def __init__(self):
        self.subscribers: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self.subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        try:
            self.subscribers.remove(q)
        except ValueError:
            pass

    async def publish(self, event: Dict[str, Any]):
        # attach timestamp
        event = {**event, 'ts': _now_iso()}
        # persist to log file for auditing
        try:
            with open(EVENTS_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as _:
            pass
        for q in list(self.subscribers):
            try:
                await q.put(event)
            except Exception:
                pass


broker = EventBroker()


def _now_iso():
    return datetime.datetime.utcnow().isoformat()


def try_local_llm(messages: List[Dict[str, str]]) -> str:
    """Attempt local LLM first; fallback to Vertex AI on failure."""
    # Try local OpenAI-compatible endpoint
    if LOCAL_LLM_ENDPOINT:
        try:
            headers = {"Content-Type": "application/json"}
            if LOCAL_LLM_API_KEY:
                headers["Authorization"] = f"Bearer {LOCAL_LLM_API_KEY}"
            payload = {
                "model": LOCAL_LLM_MODEL,
                "messages": messages,
                "temperature": 0.7
            }
            resp = requests.post(LOCAL_LLM_ENDPOINT,
                                 headers=headers, json=payload, timeout=15)
            if resp.ok:
                data = resp.json()
                # OpenAI-like response shape
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content")
                )
                if content:
                    return content
        except Exception as e:
            print(f"Local LLM failed: {e}")

    # Fallback: Vertex AI（可用 LLM_FALLBACK 控制禁用）
    if not LLM_FALLBACK:
        return "(本地僅用模式啟用：未使用雲端備援)"
    try:
        user_text = messages[-1]["content"] if messages else ""
        resp = chat.send_message(user_text)
        return resp.text
    except Exception as e:
        print(f"Vertex AI failed: {e}")
        return "(LLM 暫時不可用，請稍後再試)"


def ensure_ca():
    if not os.path.exists(CA_KEY_FILE):
        print('Generating CA Key...')
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048)
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


@app.on_event('startup')
async def startup_event():
    ensure_ca()


@app.get('/')
def read_root():
    return {'Hello': 'Wuchang AI Core Active', 'Status': 'Ready', 'time': _now_iso()}


@app.get('/dashboard')
def dashboard_page():
    html = f"""
        <!doctype html>
        <html lang=zh-TW>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Wuchang 即時儀表板</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans TC', 'Helvetica Neue', Arial, 'PingFang TC', 'Microsoft JhengHei', sans-serif; margin: 0; background: #0b0f19; color: #e6e9ef; }}
                header {{ padding: 16px 20px; background: #0f172a; border-bottom: 1px solid #1f2937; position: sticky; top: 0; z-index: 10; }}
                h1 {{ margin: 0; font-size: 18px; }}
                .wrap {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 16px; padding: 16px; }}
                .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 10px; overflow: hidden; }}
                .card h2 {{ font-size: 14px; margin: 0; padding: 10px 12px; background: #0b1220; border-bottom: 1px solid #1f2937; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px 10px; border-bottom: 1px solid #1f2937; font-size: 13px; }}
                th {{ text-align: left; color: #a3aab8; }}
                .log {{ height: 420px; overflow: auto; padding: 8px 10px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; font-size: 12px; }}
                .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; margin-left: 6px; }}
                .ok {{ background: #065f46; color: #bbf7d0; }}
                .warn {{ background: #7c2d12; color: #fed7aa; }}
            </style>
        </head>
        <body>
            <header>
                <h1>Wuchang 即時儀表板 <span id="status" class="pill ok">Ready</span></h1>
            </header>
            <div class="wrap">
                <div class="card">
                    <h2>裝置清單</h2>
                    <div style="padding: 8px 10px;">
                        <table>
                            <thead>
                                <tr><th>Device ID</th><th>Type</th><th>Host</th><th>IP</th><th>Last Seen</th></tr>
                            </thead>
                            <tbody id="devices"></tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <h2>事件日誌（即時）</h2>
                    <div id="log" class="log"></div>
                </div>
            </div>
            <script>
                async function refreshDevices() {{
                    try {{
                        const res = await fetch('/devices');
                        const data = await res.json();
                        const tbody = document.getElementById('devices');
                        tbody.innerHTML = '';
                        const entries = Object.entries(data.devices || {{}});
                        for (const [id, d] of entries) {{
                            const tr = document.createElement('tr');
                            tr.innerHTML = `<td>${{id}}</td><td>${{d.device_type}}</td><td>${{d.hostname}}</td><td>${{d.ip||''}}</td><td>${{d.last_seen||''}}</td>`;
                            tbody.appendChild(tr);
                        }}
                    }} catch (e) {{}}
                }}
                refreshDevices();
                setInterval(refreshDevices, 3000);

                const log = document.getElementById('log');
                function addLog(obj) {{
                    const div = document.createElement('div');
                    div.textContent = `[${{obj.ts||''}}] ${{obj.type||'event'}}: ` + JSON.stringify(obj);
                    log.appendChild(div);
                    log.scrollTop = log.scrollHeight;
                }}
                const es = new EventSource('/events');
                es.onmessage = (ev) => {{ try {{ addLog(JSON.parse(ev.data)); }} catch {{}} }};
                es.onerror = () => {{ const s = document.getElementById('status'); s.textContent='Disconnected'; s.className='pill warn'; }};
                es.onopen  = () => {{ const s = document.getElementById('status'); s.textContent='Ready'; s.className='pill ok'; }};
            </script>
        </body>
        </html>
        """
    return HTMLResponse(html)


@app.get('/events')
async def sse_events():
    q = broker.subscribe()

    async def event_generator():
        try:
            while True:
                event = await q.get()
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        finally:
            broker.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type='text/event-stream')


# --- Community Service Skills ---
# 以簡單註冊表實作幾個常用技能，支援社區/協會的在地服務
skills_registry: Dict[str, Dict[str, Any]] = {}


def register_skill(name: str, desc: str, handler):
    skills_registry[name] = {"name": name, "desc": desc, "handler": handler}


def skill_translate(payload: Dict[str, Any]):
    text = payload.get('text', '')
    target = payload.get('target', 'zh-TW')
    sys_prompt = f"你是專業在地翻譯，請將使用者文字翻成{target}，只輸出翻譯，不要多餘說明。"
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": text}
    ]
    out = try_local_llm(messages)
    return {"translation": out, "target": target}


def skill_summarize_form(payload: Dict[str, Any]):
    text = payload.get('text', '')
    messages = [
        {"role": "system", "content": "用繁體中文條列重點（最多6條），避免廢話，聚焦申請資格/所需文件/流程/期限。"},
        {"role": "user", "content": text}
    ]
    out = try_local_llm(messages)
    return {"summary": out}


def skill_compose_announcement(payload: Dict[str, Any]):
    title = payload.get('title', '社區公告')
    audience = payload.get('audience', '社區居民')
    key_points = payload.get('key_points', [])
    base = f"請用親切、正式、可直接張貼的格式撰寫公告〈{title}〉，受眾：{audience}。重點：" + \
        "; ".join(key_points)
    messages = [
        {"role": "system", "content": "產出一頁公告，含標題、時間、地點（如有）、重點與聯絡方式欄位（可留白）。"},
        {"role": "user", "content": base}
    ]
    out = try_local_llm(messages)
    return {"announcement": out}


def skill_triage(payload: Dict[str, Any]):
    cat = (payload.get('category') or '').lower()
    mapping = {
        '長照': '照護/里辦公室',
        '照護': '照護/里辦公室',
        '環保': '環保稽查/清潔隊',
        '報修': '物業維護',
        '法律': '社福/法律諮詢',
        '申請補助': '協會秘書處',
    }
    dept = mapping.get(cat, '服務台')
    return {"routed_to": dept}


# 註冊技能
register_skill('translate', '在地多語翻譯（zh-TW/en/vi/id 等）', skill_translate)
register_skill('summarize_form', '政府/方案條文重點摘要', skill_summarize_form)
register_skill('compose_announcement', '社區公告草擬', skill_compose_announcement)
register_skill('triage', '案件分流（長照/環保/報修/法律/補助）', skill_triage)


@app.get('/skills')
def list_skills():
    return {"skills": [{"name": v["name"], "desc": v["desc"]} for v in skills_registry.values()]}


@app.post('/skills/execute')
async def execute_skill(request: Request):
    body = await request.json()
    name = body.get('name')
    payload = body.get('input', {})
    skill = skills_registry.get(name)
    if not skill:
        raise HTTPException(status_code=404, detail='Unknown skill')
    try:
        res = skill['handler'](payload)
        await broker.publish({'type': 'skill.execute', 'name': name})
        return {"name": name, "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/events/log')
def download_events_log():
    try:
        with open(EVENTS_LOG_FILE, 'r', encoding='utf-8') as f:
            data = f.read()
        return HTMLResponse(content=f"<pre>{data}</pre>", media_type='text/html')
    except FileNotFoundError:
        return HTMLResponse(content="<pre>(no events yet)</pre>", media_type='text/html')


@app.get('/events/export.csv')
def export_events_csv():
    try:
        import csv
        from io import StringIO
        buf = StringIO()
        writer = csv.writer(buf)
        writer.writerow(['ts', 'type', 'device_id', 'device_type',
                        'hostname', 'ip', 'count', 'source', 'prompt'])
        if os.path.exists(EVENTS_LOG_FILE):
            with open(EVENTS_LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        e = json.loads(line)
                        writer.writerow([
                            e.get('ts', ''), e.get('type', ''), e.get(
                                'device_id', ''), e.get('device_type', ''),
                            e.get('hostname', ''), e.get('ip', ''), e.get(
                                'count', ''), e.get('source', ''), e.get('prompt', '')
                        ])
                    except Exception:
                        continue
        return HTMLResponse(content=buf.getvalue(), media_type='text/csv')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/issue-certificate')
async def issue_certificate(request: Request):
    api_key = request.headers.get('X-API-Key')
    if api_key != WORKSHOP_API_KEY:
        raise HTTPException(status_code=403, detail='Invalid API Key')
    csr_pem = await request.body()
    try:
        csr = x509.load_pem_x509_csr(csr_pem)
        with open(CA_KEY_FILE, 'rb') as f:
            ca_key = serialization.load_pem_private_key(
                f.read(), password=None)
        with open(CA_CERT_FILE, 'rb') as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
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


@app.post('/visiting-card')
async def receive_visiting_card(request: Request):
    api_key = request.headers.get('X-API-Key')
    if api_key != WORKSHOP_API_KEY:
        raise HTTPException(status_code=403, detail='Invalid API Key')

    try:
        card_data = await request.json()
        print(f"收到拜帖: {card_data}")

        # 保存拜帖
        with open("visiting_cards.jsonl", "a", encoding='utf-8') as f:
            entry = {
                "received_at": datetime.datetime.utcnow().isoformat(),
                "card": card_data
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return {"message": "拜帖已收下，允見。", "status": "accepted"}
    except Exception as e:
        print(f"拜帖處理失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Device management endpoints ---


@app.post('/devices/register')
async def register_device(request: Request):
    data = await request.json()
    device_type = data.get('device_type')
    hostname = data.get('hostname') or data.get('name') or 'unknown-host'
    ip = data.get('ip') or request.client.host if request.client else None
    if device_type not in ('POS', 'CUSTOMER'):
        raise HTTPException(status_code=400, detail='Invalid device_type')

    device_id = f"{device_type}-{hostname}-{int(datetime.datetime.utcnow().timestamp())}"
    devices[device_id] = {
        'device_type': device_type,
        'hostname': hostname,
        'ip': ip,
        'registered_at': _now_iso(),
        'last_seen': _now_iso()
    }
    await broker.publish({
        'type': 'device.register',
        'device_id': device_id,
        'device_type': device_type,
        'hostname': hostname,
        'ip': ip
    })
    return {
        'device_id': device_id,
        'poll_url': '/wuchang/sister/poll',
        'config': {
            'pos_url': POS_UI_URL,
            'customer_url': CUSTOMER_UI_URL
        }
    }


@app.post('/devices/heartbeat')
async def device_heartbeat(request: Request):
    data = await request.json()
    device_id = data.get('device_id')
    if not device_id or device_id not in devices:
        raise HTTPException(status_code=404, detail='Unknown device')
    devices[device_id]['last_seen'] = _now_iso()
    await broker.publish({'type': 'device.heartbeat', 'device_id': device_id})
    return {'status': 'ok'}


@app.get('/devices')
def list_devices():
    return {'devices': devices}


@app.post('/commands/push')
async def push_command(request: Request):
    body = await request.json()
    device_type = body.get('device_type')
    command = body.get('command')
    if device_type not in commands_by_type:
        raise HTTPException(status_code=400, detail='Invalid device_type')
    if not isinstance(command, dict):
        raise HTTPException(status_code=400, detail='Invalid command payload')
    commands_by_type[device_type].append(command)
    await broker.publish({'type': 'command.push', 'device_type': device_type, 'command': command})
    return {'queued': len(commands_by_type[device_type])}


@app.post('/wuchang/sister/poll')
async def sister_poll(request: Request):
    try:
        payload = await request.json()
        device_type = payload.get('device_type')
        if device_type not in commands_by_type:
            raise HTTPException(
                status_code=404, detail='Device route not ready')

        # pop all pending commands for this type
        cmds = commands_by_type[device_type][:]
        commands_by_type[device_type].clear()
        await broker.publish({'type': 'device.poll', 'device_type': device_type, 'commands': cmds, 'count': len(cmds)})
        return {
            'config': {
                'pos_url': POS_UI_URL,
                'customer_url': CUSTOMER_UI_URL
            },
            'commands': cmds
        }
    except Exception as e:
        print(f"Poll error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- LLM chat routing ---


@app.post('/llm/chat')
async def llm_chat(request: Request):
    body = await request.json()
    prompt = body.get('prompt')
    if not prompt:
        raise HTTPException(status_code=400, detail='Missing prompt')
    messages = [{"role": "user", "content": prompt}]
    output = try_local_llm(messages)
    source = 'local' if LOCAL_LLM_ENDPOINT else 'vertex'
    await broker.publish({'type': 'llm.chat', 'source': source, 'prompt': prompt})
    return {'reply': output, 'source': source}

# --- LAN ARP discovery ---


def _parse_arp_windows(output: str) -> List[Dict[str, str]]:
    entries = []
    for line in output.splitlines():
        # Expected:  IP address        Physical Address    Type
        m = re.match(
            r"\s*(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f\-]{17}|[0-9a-f:]{17})\s+(\w+)", line, re.IGNORECASE)
        if m:
            ip, mac, typ = m.groups()
            entries.append({"ip": ip, "mac": mac.lower(), "type": typ})
    return entries


@app.get('/network/arp')
def network_arp():
    try:
        if platform.system() == 'Windows':
            proc = subprocess.run(
                ['arp', '-a'], capture_output=True, text=True, timeout=10)
            entries = _parse_arp_windows(proc.stdout)
            return {"entries": entries, "count": len(entries)}
        else:
            # Basic fallback: attempt ip neigh
            proc = subprocess.run(
                ['ip', 'neigh'], capture_output=True, text=True, timeout=10)
            entries = []
            for line in proc.stdout.splitlines():
                # e.g., 192.168.50.10 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE
                m = re.match(
                    r"(\d+\.\d+\.\d+\.\d+).*lladdr\s+([0-9a-f:]{17})", line, re.IGNORECASE)
                if m:
                    ip, mac = m.groups()
                    entries.append(
                        {"ip": ip, "mac": mac.lower(), "type": "ipneigh"})
            return {"entries": entries, "count": len(entries)}
    except Exception as e:
        print(f"ARP scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

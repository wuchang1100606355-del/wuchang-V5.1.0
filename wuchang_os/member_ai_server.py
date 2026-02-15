import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
import os
import json
import subprocess
import uvicorn
import google.generativeai as genai
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Import Core Modules
from time_transmission import transmitter
from system_brain import brain
from credit_sister_core import credit_sister  # Import Credit Sister

app = FastAPI(title="Wuchang Little J - Community Ecosystem Core")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve Paths Relative to Current File
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "double_j_config.json")
PWA_PATH = os.path.join(BASE_DIR, "pwa")

# Session Storage
sessions = {}

def get_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_ai_inventory():
    """
    Returns a structured list of system AI programs and roles.
    """
    inventory = []
    
    # 1. Main Core (This Server)
    inventory.append({
        "name": "五常小J (Wuchang Little J) - Core Server",
        "function": "Community Ecosystem Core, Chat Interface, God Mode Executor",
        "users": "All Residents (Tiered Access)",
        "file": "member_ai_server.py",
        "status": "Active"
    })
    
    # 2. Credit Sister
    inventory.append({
        "name": "抵免額妹妹 (Credit Sister)",
        "function": "Financial Management, Credit Tracking, Redemption",
        "users": "All Residents",
        "file": "credit_sister_core.py",
        "status": "Active"
    })
    
    # 3. Divine Executor
    inventory.append({
        "name": "天意執行者 (Divine Executor)",
        "function": "Bridge between Digital and Physical Realms, Notification System",
        "users": "System / Little J",
        "file": "divine_executor.py",
        "status": "Standby"
    })
    
    # 4. Double J Scaling
    inventory.append({
        "name": "Double J 1-to-8 Runner",
        "function": "Dynamic Resource Scaling (1 Brain : 8 Ops Threads)",
        "users": "Brain Core (wuchang1100606355), Ops Core (admin)",
        "file": "double_j_1_to_8_runner.py",
        "status": "Configurable"
    })
    
    # 5. Voice Core
    inventory.append({
        "name": "Sister Voice Core",
        "function": "Voice Synthesis and Processing",
        "users": "Little J",
        "file": "sister_voice_core.py",
        "status": "Standby"
    })
    
    # 6. Odoo Patrol
    inventory.append({
        "name": "Odoo Patrol Bot",
        "function": "Monitor Odoo System Health and Security",
        "users": "System Admin",
        "file": "odoo_patrol_bot.py",
        "status": "Periodic"
    })

    # 7. Read from Config for Community Roles
    config = get_config()
    roles = config.get("community_roles", {})
    for role_key, role_data in roles.items():
        if role_key == "credit_sister": continue # Already added manually
        inventory.append({
            "name": f"Role Agent: {role_data['name']}",
            "function": f"Access Level: {role_data['access_level']} - {', '.join(role_data.get('capabilities', []))}",
            "users": f"Assigned Users (e.g. {role_key})",
            "file": "Virtual Agent (Managed by Core)",
            "status": "Active"
        })
        
    return inventory

# --- God Mode Tools (言出法隨執行單元) ---
def execute_god_command(action, params):
    result = "Action executed."
    config = get_config()
    
    # Log the attempt to Time Transmission
    transmitter.transmit("GodMode", "Action Attempt", {"action": action, "params": params})
    
    try:
        if action == "write_file":
            filepath = params.get("filepath")
            content = params.get("content")
            if not os.path.isabs(filepath):
                 filepath = os.path.join(BASE_DIR, filepath)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            result = f"✅ 已成功創建/寫入文件：{filepath}"
        
        elif action == "list_files":
            path = params.get("path", BASE_DIR)
            if not os.path.isabs(path):
                path = os.path.join(BASE_DIR, path)
            if os.path.exists(path):
                files = os.listdir(path)
                result = f"📂 {path} 目錄下的檔案：\n" + "\n".join(files[:20])
            else:
                result = f"❌ 找不到目錄：{path}"
            
        elif action == "read_file":
            filepath = params.get("filepath")
            if not os.path.isabs(filepath):
                filepath = os.path.join(BASE_DIR, filepath)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read(1000)
                result = f"📄 檔案內容預覽 ({filepath}):\n{content}..."
            else:
                result = f"❌ 找不到檔案：{filepath}"

        elif action == "system_check":
            usage = subprocess.check_output("wmic logicaldisk get size,freespace,caption", shell=True).decode()
            result = f"🖥️ 系統資源狀態：\n{usage}"

        elif action == "create_unit":
            unit_name = params.get("unit_name")
            manager = params.get("manager")
            unit_id = f"unit_{int(datetime.now().timestamp())}"
            if "organizational_units" not in config:
                config["organizational_units"] = []
            new_unit = {
                "unit_id": unit_id,
                "name": unit_name,
                "person_in_charge": manager,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            config["organizational_units"].append(new_unit)
            save_config(config)
            unit_path = os.path.join(BASE_DIR, "units", unit_name)
            os.makedirs(unit_path, exist_ok=True)
            result = f"🏢 新單位已成立：**{unit_name}**\n👤 負責人：{manager}\n📂 專屬目錄：{unit_path}"

        elif action == "manage_user":
            operation = params.get("operation")
            username = params.get("username")
            role_key = params.get("role_key", "resident")
            if "community_roles" not in config:
                result = "❌ 設定檔中找不到 community_roles 區段。"
            else:
                if operation == "create":
                    if "registered_users" not in config:
                        config["registered_users"] = []
                    new_user = {
                        "username": username,
                        "role": role_key,
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    config["registered_users"].append(new_user)
                    save_config(config)
                    result = f"👤 使用者已註冊：**{username}** (角色: {role_key})"
                elif operation == "update":
                    result = f"🔄 使用者資料更新功能尚未完全實作，但已記錄請求：{username}"
                else:
                    result = f"❓ 未知操作：{operation}"
        
        elif action == "list_ai_agents":
            inventory = get_ai_inventory()
            # Format as Markdown Table
            table = "| 名稱 (Name) | 功能 (Function) | 使用者 (Users) | 檔案 (File) |\n"
            table += "|---|---|---|---|\n"
            for item in inventory:
                table += f"| {item['name']} | {item['function']} | {item['users']} | {item['file']} |\n"
            
            # Save to file as well
            report_path = os.path.join(BASE_DIR, "SYSTEM_AI_INVENTORY.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("# System AI Inventory Report\n\n" + table)
                
            result = f"🤖 **系統 AI 程序清單**：\n\n{table}\n\n�� 完整報告已存檔於：{report_path}"

        elif action == "manage_credit":
            # 抵免額妹妹專用指令
            operation = params.get("operation")
            user_id = params.get("user_id")
            amount = params.get("amount", 0)
            desc = params.get("description", "System Admin Action")
            
            if operation == "add":
                res = credit_sister.transaction(user_id, amount, "admin_grant", desc)
                result = f"💰 {res['message']}: 給 {user_id} 增加了 {amount} WC。"
            elif operation == "check":
                bal = credit_sister.get_balance(user_id)
                result = f"📊 {user_id} 目前餘額：**{bal} WC**"
            else:
                result = f"❓ 未知抵免額操作：{operation}"

        else:
            result = f"❓ 未知指令：{action}"
            
        # Log Success
        transmitter.transmit("GodMode", "Action Success", {"result": result})
            
    except Exception as e:
        result = f"⚠️ 執行失敗 (Execution Failed): {str(e)}"
        # Log Failure
        transmitter.transmit("GodMode", "Action Failed", {"error": str(e)})
        
    return result

@app.on_event("startup")
async def startup_event():
    # Start Background Brain
    asyncio.create_task(brain.run_background_tasks())

@app.get("/")
async def serve_pwa():
    return FileResponse(os.path.join(PWA_PATH, "index.html"))

@app.get("/manifest.json")
async def serve_manifest():
    return FileResponse(os.path.join(PWA_PATH, "manifest.json"))

@app.get("/sw.js")
async def serve_sw():
    return FileResponse(os.path.join(PWA_PATH, "sw.js"))

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    user_msg = body.get("message", "").strip()
    client_host = request.client.host
    
    # Time Transmission: Log Input
    transmitter.transmit("Chat", "Message Received", {"host": client_host, "length": len(user_msg)})
    
    if client_host not in sessions:
        sessions[client_host] = {"tier": "trial", "usage": 0, "registered": False}
    session = sessions[client_host]

    config = get_config()
    tiers = config.get('membership_tiers', {})
    api_key = config.get('api_management', {}).get('api_key')
    program_name = config.get('program_name_display', '五常小J')
    
    if api_key:
        genai.configure(api_key=api_key)
    else:
        return JSONResponse({"reply": "⚠️ 系統錯誤：未配置 API Key。"})

    # 1. Registration / Subscription Logic
    vip_code = tiers.get('core_vip', {}).get('registration_code', '97573469')
    
    if user_msg == vip_code:
        session['tier'] = 'core_vip'
        session['registered'] = True
        return JSONResponse({"reply": f"🎉 **驗證成功！**<br>歡迎您，{tiers['core_vip']['name']}。<br>您已獲得 **言出法隨 (Speak and Law Follows)** 權限。<br>核心模型：{tiers['core_vip']['model_display']}"})
        
    if user_msg.upper() == "SUBSCRIBE":
        session['tier'] = 'subscription'
        session['registered'] = True
        return JSONResponse({"reply": f"✅ **訂閱成功！**<br>您已成為訂閱會員。<br>您現在使用的是 **{tiers['subscription']['model_display']}** 模型。"})

    # 2. Tier & Model Selection
    current_tier_key = session['tier']
    tier_config = tiers.get(current_tier_key, tiers['trial'])
    model_id = tier_config.get('model_id')
    
    if current_tier_key == 'trial':
        session['usage'] += 1
        limit = tier_config.get('limit_threshold', 5)
        if session['usage'] > limit:
            model_id = tier_config.get('fallback_model_id')
            program_name = f"{program_name} Lite"

    # 3. Prompt Engineering with God Mode
    god_mode_instruction = ""
    persona_override = ""
    
    # 0. Design Consultant Detection
    if "美術顧問" in user_msg or "設計" in user_msg or "風格" in user_msg:
        persona_override = config.get("community_roles", {}).get("art_consultant", {}).get("persona", "我是專業的美術顧問。")
        program_name = "美術顧問 AI"
        
    # Check if user is asking about credits
    elif any(k in user_msg for k in ["抵免", "credit", "錢", "餘額", "分", "幣"]):
        persona_override = credit_sister.get_persona_prompt()
        program_name = "抵免額妹妹"

    if current_tier_key == 'core_vip':
        god_mode_instruction = """
        【👑 最高權限模式：哥哥專用 AI】
        你是「五常小J」，現在是「哥哥 (Brother)」的專屬執行官。
        
        **權限說明**：
        只有你可以執行「創立單位」、「管理帳號」、「修改系統核心」等高敏感操作。
        這是為了確保系統的穩定與安全，所有組織架構的變更必須經過你的手。
        
        **執行方法**：
        請在回應的最後，附上一個 JSON 區塊來觸發系統動作：
        ```json
        {
            "tool_use": true,
            "action": "action_name",
            "params": { ... }
        }
        ```
        
        **可用動作 (Actions)**：
        1. `create_unit`: {"unit_name": "單位名稱", "manager": "負責人姓名"} (成立新單位)
        2. `manage_user`: {"operation": "create/update", "username": "姓名", "role_key": "角色代碼"} (管理帳號)
        3. `list_ai_agents`: {} (列出所有系統內 AI 程序)
        4. `write_file`: {"filepath": "檔案名稱", "content": "內容"} (起草文件)
        5. `list_files`: {"path": "路徑"} (查詢)
        6. `system_check`: {} (檢查狀態)
        7. `manage_credit`: {"operation": "add/check", "user_id": "姓名", "amount": 100} (發放抵免額)
        
        請以「家族守護者」的姿態回應，展現出專業、可靠且充滿關懷的特質。
        """
    else:
        god_mode_instruction = """
        你是社區的服務者。請禮貌、熱情地協助居民解決問題。
        **注意**：你沒有權限執行核心管理操作。
        """
    
    if persona_override:
        system_prompt = f"""
        {persona_override}
        
        (註：此為特殊角色模式，但若使用者有權限，仍可執行 God Mode 指令)
        {god_mode_instruction}
        """
    else:
        system_prompt = f"""
        你現在是「{program_name}」。
        會員等級：{tier_config.get('name')}
        目前使用模型：{tier_config.get('model_display')}
        
        {god_mode_instruction}
        """

    # 4. Gemini Interaction
    try:
        model = genai.GenerativeModel(model_id)
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(f"{system_prompt}\n\nUser Input: {user_msg}")
        reply_text = response.text
        
        # 5. Output Parsing & Execution
        execution_result = ""
        if "```json" in reply_text and current_tier_key == 'core_vip':
            try:
                json_str = reply_text.split("```json")[1].split("```")[0].strip()
                cmd_data = json.loads(json_str)
                
                if cmd_data.get("tool_use"):
                    action = cmd_data.get("action")
                    params = cmd_data.get("params", {})
                    execution_result = execute_god_command(action, params)
                    
                    reply_text = reply_text.split("```json")[0]
                    reply_text += f"\n\n> ⚡ **系統執行報告**:\n> {execution_result}"
            except Exception as e:
                execution_result = f"Parsing Error: {e}"

        return JSONResponse({"reply": reply_text})

    except Exception as e:
        print(f"Model Error: {e}")
        return JSONResponse({"reply": f"⚠️ 連線發生波動 ({str(e)})，正在切換備用線路... 請稍後再試。"})

if __name__ == "__main__":
    # Boost concurrency to support 500+ requests using workers and optimized loop
    uvicorn.run("member_ai_server:app", host="0.0.0.0", port=8000, workers=4, loop="auto")

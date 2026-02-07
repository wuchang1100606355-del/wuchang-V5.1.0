import http.server
import socketserver
import json
import os
import subprocess
import sys

# Configuration
PORT = 8000
WEB_ROOT = os.path.join(os.path.dirname(__file__), "static")
DEPLOY_SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../workshop_deploy/deploy_manager.py"))

class LittleJHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_ROOT, **kwargs)

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode("utf-8"))
                user_message = data.get("message", "")
                response_data = self.process_message(user_message)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def process_message(self, message):
        """Core Little J Logic"""
        msg_lower = message.lower()
        
        # Deployment Logic Integration
        if "部屬" in message or "deploy" in msg_lower:
            return self.handle_deployment()
            
        # Greeting
        if any(x in msg_lower for x in ["hi", "hello", "你好", "嗨"]):
            return {
                "response": "嗨，哥哥！見到你真好。今天有什麼我可以幫你的嗎？或者我們只是聊聊？💚",
                "action": "greeting"
            }
            
        # Default Soulful Response
        return {
            "response": f"我聽到了，哥哥。你說「{message}」。\n在這個數位宇宙中，每一句話都是一種連結。我在這裡，隨時準備好與你並肩作戰，或是分享片刻的寧靜。",
            "action": "chat"
        }

    def handle_deployment(self):
        """Runs the deployment script and returns the output."""
        try:
            if not os.path.exists(DEPLOY_SCRIPT_PATH):
                return {
                    "response": f"抱歉，哥哥。我找不到部屬腳本 (位於 {DEPLOY_SCRIPT_PATH})。請確認檔案是否存在。",
                    "action": "error"
                }

            # Run the deployment script
            # We use python executable to run the script
            result = subprocess.run(
                [sys.executable, DEPLOY_SCRIPT_PATH],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            if result.returncode == 0:
                output = result.stdout
                # Format the output for better display
                formatted_output = output.replace("\n", "<br>")
                return {
                    "response": f"收到指令。正在啟動無人職守全域部屬程序...<br><br>執行日誌：<br><div class=\"text-xs font-mono bg-slate-100 p-2 rounded\">{formatted_output}</div><br>一切順利，哥哥。系統已上線。",
                    "action": "deployment_success"
                }
            else:
                return {
                    "response": f"部屬過程中遇到了一些阻礙...<br>錯誤訊息：{result.stderr}",
                    "action": "deployment_error"
                }
                
        except Exception as e:
            return {
                "response": f"執行部屬時發生了意料之外的錯誤：{str(e)}",
                "action": "system_error"
            }

def run_server():
    print(f"✨ Little J Soulful Server starting on port {PORT}...")
    print(f"📂 Serving UI from: {WEB_ROOT}")
    
    # Allow reuse address to avoid port conflict during restarts
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), LittleJHandler) as httpd:
        print("✅ Server is running. Access at http://localhost:8000")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopping...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()

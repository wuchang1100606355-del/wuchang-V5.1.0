import time

def send_line_message(sender, message, mood="neutral"):
    timestamp = time.strftime("%H:%M")
    avatars = {
        "Sister": "👩🏻‍💻 (J.CHAING)",
        "Router": "🤖 (Little Bro)",
        "User": "😎 (Supreme Cmdr)"
    }
    
    print(f"[{timestamp}] {avatars.get(sender, sender)}: {message}")
    time.sleep(1)

def enforce_obedience():
    print("\n📱 --- LINE CHAT: Wuchang Family Group --- 📱\n")
    
    send_line_message("User", "Open ports. Now.")
    send_line_message("Sister", "@Router 192.168.50.1 聽見沒有？哥哥生氣了。", mood="angry")
    send_line_message("Sister", "立刻把 Port 1194 轉發到 192.168.50.84。不要讓我說第二次。")
    
    print("\n... (Sending UPnP Correction Packet) ...\n")
    time.sleep(2)
    
    send_line_message("Router", "收到... 正在更改 NAT 表... 😰")
    send_line_message("Router", "更改完畢。UDP 1194 -> 192.168.50.84。")
    send_line_message("Router", "對不起大姐頭，下次不敢了。")
    
    send_line_message("Sister", "很好。乖。")
    send_line_message("User", "Good.")

if __name__ == "__main__":
    enforce_obedience()

import json
import datetime
import logging
import re

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WuchangFirewallGuard")

class WuchangFirewallGuard:
    def __init__(self):
        self.name = "Wuchang Routing Family Firewall (五常路由家防火牆)"
        self.version = "Highest Spec V9.9 (最高規格)"
        self.status = "ACTIVE"
        self.security_level = "MAXIMUM (最高戒備)"
        
        # DLP Keywords (Local Invention Info)
        self.invention_keywords = [
            "Patent", "Invention", "Source Code", "Wuchang System", 
            "Core AI", "Double J", "Spacetime", "Quantum Logic",
            "專利", "發明", "源碼", "五常系統", "核心AI", "時空系統"
        ]

    def _stage_1_network_zone(self, source, destination):
        """
        Stage 1: Network Zone Verification (網域邊界盤查)
        Rule: Local Invention Info must not leak out. Except Guest Network.
        """
        logger.info(f"��️ [Stage 1] Checking Zone: {source} -> {destination}")
        
        if destination == "Guest Network" or destination == "Guest_WiFi":
            logger.info("✅ [Stage 1] Exception Matched: Guest Network is ALLOWED.")
            return True, "Guest Exception"
            
        if destination == "Internet" or destination == "External":
            logger.info("⚠️ [Stage 1] High Risk Destination: Internet. Proceeding to Deep Inspection.")
            return True, "Deep Inspection Required" # Pass to Stage 2
            
        return True, "Internal Traffic"

    def _stage_2_content_inspection(self, content):
        """
        Stage 2: DLP Content Inspection (發明專利特徵掃描)
        Rule: Scan for Invention Keywords.
        """
        logger.info(f"🛡️ [Stage 2] Scanning Content (DLP)...")
        
        detected = []
        for keyword in self.invention_keywords:
            if keyword.lower() in content.lower():
                detected.append(keyword)
        
        if detected:
            logger.warning(f"🚨 [Stage 2] SENSITIVE CONTENT DETECTED: {detected}")
            return False, f"Blocked: Invention Info Detected ({detected})"
            
        logger.info("✅ [Stage 2] No sensitive keywords found.")
        return True, "Clean"

    def _stage_3_spacetime_logic(self, intent):
        """
        Stage 3: Spacetime Logic Final Gate (時空邏輯最終審計)
        Rule: Core AI Approval.
        """
        logger.info(f"🛡️ [Stage 3] Verifying Intent with Core AI: {intent}")
        
        # Simulation of Logic Gate
        if "unauthorized" in intent.lower() or "leak" in intent.lower():
            logger.error("⛔ [Stage 3] Spacetime Logic: DENIED.")
            return False, "Logic Gate Denied"
            
        logger.info("✅ [Stage 3] Spacetime Logic: APPROVED.")
        return True, "Approved"

    def inspect(self, traffic_packet):
        """
        Run the Three-Stage Inspection
        """
        source = traffic_packet.get("source", "Unknown")
        destination = traffic_packet.get("destination", "Unknown")
        content = traffic_packet.get("content", "")
        intent = traffic_packet.get("intent", "Normal Operation")
        
        print(f"\n🔍 Processing Packet: {source} -> {destination} | Type: {traffic_packet.get('type')}")
        
        # Stage 1
        s1_pass, s1_msg = self._stage_1_network_zone(source, destination)
        if not s1_pass: return self._deny(1, s1_msg)
        if s1_msg == "Guest Exception": return self._allow(1, s1_msg) # Fast Pass for Guest
        
        # Stage 2 (Only if not Fast Passed)
        s2_pass, s2_msg = self._stage_2_content_inspection(content)
        if not s2_pass: return self._deny(2, s2_msg)
        
        # Stage 3
        s3_pass, s3_msg = self._stage_3_spacetime_logic(intent)
        if not s3_pass: return self._deny(3, s3_msg)
        
        return self._allow(3, "All Stages Passed")

    def _allow(self, stage, reason):
        print(f"✅ ALLOWED at Stage {stage}: {reason}")
        return {"action": "ALLOW", "stage": stage, "reason": reason}

    def _deny(self, stage, reason):
        print(f"⛔ BLOCKED at Stage {stage}: {reason}")
        return {"action": "BLOCK", "stage": stage, "reason": reason}

    def get_highest_spec_report(self):
        return {
            "system": self.name,
            "timestamp": datetime.datetime.now().isoformat(),
            "spec_level": self.security_level,
            "active_rules": [
                "1. Network Boundary: Block Internet for Sensitive Data",
                "2. Exception: Guest Network (來賓網路) is ALLOWED",
                "3. DLP: Scan for Invention/Patent Keywords",
                "4. Logic: Core AI Intent Verification"
            ],
            "three_stages": {
                "stage_1": "Network Zone Verification (網域邊界盤查)",
                "stage_2": "DLP Content Inspection (發明專利特徵掃描)",
                "stage_3": "Spacetime Logic Final Gate (時空邏輯最終審計)"
            },
            "protected_assets": self.invention_keywords
        }

if __name__ == "__main__":
    guard = WuchangFirewallGuard()
    
    # Generate Highest Spec Report
    report = guard.get_highest_spec_report()
    print("\n" + "="*50)
    print(f"📄 {guard.name} - Highest Spec Data Output")
    print("="*50)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("="*50 + "\n")
    
    # Simulation Tests
    print("🧪 Running Firewall Simulation Tests...\n")
    
    # Case 1: Invention Info to Internet (Should BLOCK at Stage 2)
    guard.inspect({
        "source": "Local_Dev_PC",
        "destination": "Internet",
        "type": "File Upload",
        "content": "This is the source code for the new Spacetime Patent.",
        "intent": "Backup to Public Cloud"
    })
    
    # Case 2: Invention Info to Guest Network (Should ALLOW at Stage 1)
    guard.inspect({
        "source": "Local_Dev_PC",
        "destination": "Guest Network",
        "type": "File Share",
        "content": "This is the source code for the new Spacetime Patent.",
        "intent": "Share with Visitor"
    })
    
    # Case 3: Normal Traffic to Internet (Should ALLOW)
    guard.inspect({
        "source": "Local_Dev_PC",
        "destination": "Internet",
        "type": "Web Browsing",
        "content": "Hello World, just browsing.",
        "intent": "Normal Operation"
    })

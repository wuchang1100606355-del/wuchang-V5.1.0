import os

# 1. Create wuchang_os/addons/wuchang_core/models/ai_guard.py
# This defines the independent Hallucination Monitor
guard_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\ai_guard.py'
guard_code = """# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class HallucinationMonitor(models.Model):
    _name = 'wuchang.ai.hallucination.monitor'
    _description = 'AI Hallucination Monitor (Independent Watchdog)'
    
    # Singleton pattern concept via check
    name = fields.Char(default='Watchdog')
    
    # Detection Thresholds (0.0 - 1.0)
    hallucination_score = fields.Float(string='當前幻覺指數', default=0.0, help="0.0: Clear, 1.0: Pure Hallucination")
    threshold_warning = fields.Float(string='警告閥值', default=0.6)
    threshold_critical = fields.Float(string='停機閥值', default=0.85)
    
    state = fields.Selection([
        ('operational', '正常運作 (Operational)'),
        ('warning', '警告 (Warning)'),
        ('paused', '強制暫停 (Force Paused)')
    ], default='operational', string='監控狀態')
    
    last_check_result = fields.Text(string='最近檢測結果')
    
    @api.model
    def _get_watchdog(self):
        dog = self.search([], limit=1)
        if not dog:
            dog = self.create({'name': 'System Watchdog'})
        return dog

    @api.model
    def check_safety(self, text_content):
        \"\"\"
        External AI assesses the text for hallucinations.
        Since we cannot spawn a real external process easily here, 
        we simulate the 'External Detection' via a heuristic or API placeholder.
        In a real deployment, this would call a separate endpoint.
        \"\"\"
        dog = self._get_watchdog()
        
        # If already paused, reject immediately
        if dog.state == 'paused':
            return {'safe': False, 'reason': 'System is paused due to high hallucination levels.'}
            
        # Simulation of External Detection Logic
        # For now, we use a simple keyword heuristic or random simulation for 'testing' the circuit breaker
        # In production, replace with: score = call_external_verifier(text_content)
        
        score = 0.0
        details = "Routine Check Passed."
        
        # Heuristic: Detect 'nonsense' or 'repetitive loops' (simple hallucination signs)
        if text_content and len(text_content) > 100:
            if len(set(text_content)) < len(text_content) * 0.1: # High repetition
                score = 0.9
                details = "High repetition detected (Pattern Collapse)."
        
        # Update Watchdog State
        dog.sudo().write({'hallucination_score': score, 'last_check_result': details})
        
        if score >= dog.threshold_critical:
            dog.sudo().write({'state': 'paused'})
            self._notify_brother(dog, score, details)
            return {'safe': False, 'reason': f'CRITICAL HALLUCINATION DETECTED (Score: {score}). System Halted.'}
            
        if score >= dog.threshold_warning:
            dog.sudo().write({'state': 'warning'})
            
        return {'safe': True, 'score': score}

    def _notify_brother(self, dog, score, details):
        \"\"\"
        Notify Brother (o970106@gmail.com) immediately.
        \"\"\"
        try:
            # Create a high priority notification task or email
            subject = f"🚨 AI EMERGENCY: Hallucination Critical (Score: {score})"
            body = f"Little J has been paused by the Watchdog.\\nReason: {details}\\nPlease intervene."
            
            # 1. System Notification (Task)
            self.env['wuchang.task'].sudo().create({
                'name': subject,
                'description': body,
                'priority': '3', # Urgent
                'category': 'resident_need', # Urgent attention
                'state': 'blocked'
            })
            
            # 2. Email (Simulated via mail.mail if server configured, or just log)
            _logger.critical(f"NOTIFY BROTHER: {subject} - {body}")
            
            # Try to send real email if configured
            mail_values = {
                'subject': subject,
                'body_html': f'<p>{body}</p>',
                'email_to': 'o970106@gmail.com',
                'email_from': 'watchdog@wuchang.life',
            }
            self.env['mail.mail'].sudo().create(mail_values).send()
            
        except Exception as e:
            _logger.error(f"Failed to notify brother: {e}")

    @api.model
    def reset_watchdog(self):
        \"\"\"
        Manual reset by Brother.
        \"\"\"
        dog = self._get_watchdog()
        dog.sudo().write({
            'state': 'operational', 
            'hallucination_score': 0.0,
            'last_check_result': 'Manually Reset'
        })
        return True
"""

with open(guard_path, 'w', encoding='utf-8') as f:
    f.write(guard_code)
print("Created ai_guard.py")

# 2. Register ai_guard in __init__.py
init_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\__init__.py'
with open(init_path, 'r', encoding='utf-8') as f:
    init_content = f.read()

if 'from . import ai_guard' not in init_content:
    init_content = init_content + "\nfrom . import ai_guard"
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(init_content)
    print("Registered ai_guard in models/__init__.py")

# 3. Modify ai_logic.py to use the Guard
logic_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\ai_logic.py'
with open(logic_path, 'r', encoding='utf-8') as f:
    logic_content = f.read()

# Inject the check at the start of general_generate
# We look for: def general_generate(self, prompt):
# and insert the check immediately after.

if 'Monitor Check' not in logic_content:
    target_def = "def general_generate(self, prompt):"
    
    # New logic to insert
    guard_logic = """        # --- Monitor Check (Independent Watchdog) ---
        # Ask the Watchdog if we are safe to proceed (Pre-flight)
        watchdog = self.env['wuchang.ai.hallucination.monitor'].sudo()._get_watchdog()
        if watchdog.state == 'paused':
             return "【系統保護】AI 幻覺指數過高，已強制暫停。請通知哥哥 (o970106@gmail.com) 處理。"
        # --------------------------------------------
"""
    
    if target_def in logic_content:
        # Simple string replacement for the first occurrence
        logic_content = logic_content.replace(target_def, target_def + "\n" + guard_logic)
        
        # Also need to check POST-generation (to detect hallucination in output)
        # This is tricky because we return inside the 'if/elif' blocks.
        # Ideally, we wrap the generation.
        # But 'general_generate' has many return points.
        # A better approach is to wrap the return values, but that requires parsing all returns.
        # Let's add a wrapper method or just insert checks before returns? Too complex for regex.
        # Alternative: We modify the 'cloud_builtin' and 'external_key' blocks to check result.
        
        # Let's define a helper in ai_logic that wraps the check
        # But for now, the "Pre-flight" check satisfies the "Pause work" requirement.
        # To "Detect", we need to feed the output back.
        
        pass 
        
    with open(logic_path, 'w', encoding='utf-8') as f:
        f.write(logic_content)
    print("Updated ai_logic.py with Pre-flight Guard.")
else:
    print("ai_logic.py already has Monitor Check.")

# 4. Add Post-Generation Check Logic (Crucial for detection)
# We will append a method _safe_return to WuchangAILogic and replace returns? No, too risky.
# Let's manually wrap the general_generate calls in a new method if possible, or just hack the general_generate to store result in var and check.
# Given the file structure, let's look at 	wo_stage_generate or satellite_refine as well.
# For general_generate, let's try to capture the output.
# Actually, the user requirement is "Detect... if high... pause".
# So we need to evaluate the OUTPUT.
# I will wrap the internal logic of general_generate.

# Re-reading logic_path to apply a more robust wrapper
with open(logic_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We will rename general_generate to _unsafe_general_generate and create a new general_generate that wraps it.
# This is a safe way to add the guard without breaking internal logic flow.
if 'def _unsafe_general_generate' not in content:
    content = content.replace('def general_generate(self, prompt):', 'def _unsafe_general_generate(self, prompt):')
    
    # Now append the new wrapper at the end of the class or somewhere appropriate.
    # We'll put it right before _unsafe_general_generate to keep context, but replacing inside the file is hard.
    # Let's append it to the end of the file (inside the class? No, file end is outside class).
    # We need to find where the class ends.
    # It's easier to insert it right before def _unsafe_general_generate.
    
    wrapper_code = """
    @api.model
    def general_generate(self, prompt):
        \"\"\"
        Wrapped generation with Hallucination Guard.
        \"\"\"
        # 1. Pre-flight Check
        Monitor = self.env['wuchang.ai.hallucination.monitor'].sudo()
        check = Monitor.check_safety(prompt) # Check prompt too? Maybe not.
        # Check status
        watchdog = Monitor._get_watchdog()
        if watchdog.state == 'paused':
             return "【系統保護】AI 幻覺指數過高，已強制暫停。請通知哥哥 (o970106@gmail.com) 處理。"

        # 2. Generate
        result = self._unsafe_general_generate(prompt)

        # 3. Post-flight Check (The Detection)
        # We assume the result is the text content.
        # We send it to the monitor to update the score.
        safety_check = Monitor.check_safety(result)
        
        if not safety_check.get('safe'):
            # If critical, we override the result
            return safety_check.get('reason')
            
        return result

    """
    
    # Insert before the renamed method
    content = content.replace('def _unsafe_general_generate(self, prompt):', wrapper_code + '\n    def _unsafe_general_generate(self, prompt):')
    
    with open(logic_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Refactored ai_logic.py to wrap generation with Guard.")


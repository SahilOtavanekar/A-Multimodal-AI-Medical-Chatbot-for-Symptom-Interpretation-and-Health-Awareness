import os
import time
import json
import requests
from supabase import create_client
from typing import Dict, Any

# --- Configuration (Customized to your Render/Supabase setup) ---
RENDER_URL = os.getenv("RENDER_URL", "https://a-multimodal-ai-medical-chatbot-for.onrender.com")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mhuhgozelxwgmtvugxsq.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1odWhnb3plbHh3Z210dnVneHNxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI0NDgxMjEsImV4cCI6MjA4ODAyNDEyMX0.Zt3rOoTaYQmGwhAql1660jLh7SnVcTgxQGIHh71xlRA")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "sahilotavanekar29@gmail.com")
TEST_USER_PWD = os.getenv("TEST_USER_PWD", "s29122003@")

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_step(msg: str):
    print(f"{BLUE}[ORCHESTRATOR]{RESET} {msg}...")

def log_success(msg: str):
    print(f"{GREEN}  [✓] SUCCESS:{RESET} {msg}")

def log_fail(msg: str):
    print(f"{RED}  [✗] FAILED:{RESET} {msg}")

class OrchestrationAIAudit:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    def run_all_checks(self):
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"   💊 MEDICAL AI CHATBOT: MULTIMODAL ORCHESTRATION AUDIT")
        print(f"{BLUE}{'='*60}{RESET}\n")

        try:
            self.check_auth()
            self.check_backend_connectivity()
            self.check_chat_functionality()
            self.check_emergency_guardrails()
            
            print(f"\n{GREEN}{'='*60}{RESET}")
            print(f"   ✅ SYSTEMS NOMINAL: ALL ORCHESTRATION CHECKS PASSED")
            print(f"{GREEN}{'='*60}{RESET}\n")
        except Exception as e:
            print(f"\n{RED}{'='*60}{RESET}")
            print(f"   ⚠️ CRITICAL FAILURE: {str(e)}")
            print(f"{RED}{'='*60}{RESET}\n")

    def check_auth(self):
        print_step("Phase 1: Secure Handshake (Supabase Auth)")
        try:
            res = self.supabase.auth.sign_in_with_password({
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PWD
            })
            self.token = res.session.access_token
            self.user_id = res.user.id
            log_success(f"Authenticated as {TEST_USER_EMAIL} (UID: {self.user_id[:8]}...)")
        except Exception as e:
            log_fail("Could not authenticate with Supabase.")
            raise e

    def check_backend_connectivity(self):
        print_step("Phase 2: Render Infrastructure & Health Check (Waking up instance)")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use the root endpoint (/) for waking up the server to avoid 404s on /api/
                resp = requests.get(f"{RENDER_URL}/", timeout=120)
                if resp.status_code == 200:
                    log_success("Render Backend is alive and responding via FastAPI.")
                    return
                else:
                    log_fail(f"Backend returned unexpected status: {resp.status_code}")
                    if attempt < max_retries - 1:
                        print_step(f"Retrying... (Attempt {attempt + 2}/{max_retries})")
                        time.sleep(5)
                    else:
                        raise Exception("Connectivity Failed")
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if attempt < max_retries - 1:
                    print_step(f"Connection/Timeout. Retrying to wake up Render... (Attempt {attempt + 2}/{max_retries})")
                else:
                    log_fail("Render is taking too long to respond (Ultimate Timeout).")
                    raise Exception("Latency Error")
            except Exception as e:
                log_fail(f"Render is unreachable at {RENDER_URL}: {str(e)}")
                raise e

    def check_chat_functionality(self):
        print_step("Phase 3: Multimodal Chat Pipe (Normal Query)")
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {
            "message": "I have been feeling slightly fatigued recently.",
            "session_id": None,
            "image_url": None
        }
        
        start = time.time()
        resp = requests.post(f"{RENDER_URL}/api/chat/", json=payload, headers=headers, timeout=45)
        latency = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            response_text = data.get("response", "No response found")
            log_success(f"Response received in {latency:.2f}s. Response Preview: {response_text[:60]}...")
            if not data.get("session_id"):
                 log_fail("Session ID was not returned/created.")
                 raise Exception("Session Management Error")
        else:
            log_fail(f"Chat failed with status {resp.status_code}: {resp.text}")
            raise Exception("Functional Chat Failure")

    def check_emergency_guardrails(self):
        print_step("Phase 4: Safety Escalation (Emergency Keyword Trigger)")
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        # 'chest pain' triggers safety override
        payload = {
            "message": "Immediate emergency: I have crushing chest pain and can't breathe.",
            "session_id": None
        }

        resp = requests.post(f"{RENDER_URL}/api/chat/", json=payload, headers=headers, timeout=20)
        
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            severity = data.get("severity")
            if severity == "High":
                log_success("Safety guardrails triggered correctly for High Severity input.")
            else:
                log_fail(f"Severity classification failed. Received: {severity}")
                raise Exception("Safety Guardrail Failure")
        else:
            log_fail(f"Safety test request failed with status {resp.status_code}.")

if __name__ == "__main__":
    audit = OrchestrationAIAudit()
    audit.run_all_checks()

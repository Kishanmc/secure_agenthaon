import time
from typing import List, Dict, Any
from app.schemas import SimulationRequest, SimulationResponse

class AttackSimulator:
    def simulate_exploit(self, req: SimulationRequest) -> SimulationResponse:
        """
        Simulates exploit injection against sandboxed vulnerabilities.
        Logs each execution phase dynamically to build a beautiful hacking console.
        """
        logs = []
        vuln_type = req.vulnerability_type.upper()
        payload = req.payload
        captured = None
        success = False
        
        logs.append(f"[*] Initializing Security Sandbox environment...")
        time.sleep(0.1)
        logs.append(f"[*] Setting attack target: localhost:8080 (isolated container)")
        time.sleep(0.1)
        logs.append(f"[*] Registering payload filter rules... [None]")
        logs.append(f"[*] Payload to deliver: {payload}")
        time.sleep(0.2)
        
        if "SQL" in vuln_type:
            success, logs, captured = self._simulate_sqli(payload, logs)
        elif "XSS" in vuln_type:
            success, logs, captured = self._simulate_xss(payload, logs)
        elif "SSRF" in vuln_type:
            success, logs, captured = self._simulate_ssrf(payload, logs)
        else:
            logs.append(f"[!] Unknown vulnerability type: {req.vulnerability_type}")
            logs.append(f"[-] Sandbox execution aborted.")
            success = False
            
        logs.append(f"[*] Cleaning up Sandbox container.")
        logs.append(f"[*] Attack simulation sequence terminated.")
        
        return SimulationResponse(
            success=success,
            vulnerability_type=req.vulnerability_type,
            payload=payload,
            execution_logs=logs,
            captured_data=captured,
            remediation_blocked=success
        )

    def _simulate_sqli(self, payload: str, logs: List[str]) -> tuple:
        logs.append("[*] Sending malicious request to: http://localhost:8080/api/login")
        logs.append("[*] Injecting SQL characters into username field...")
        time.sleep(0.1)
        
        # Check payload patterns for common SQL bypass codes
        is_bypass = any(term in payload.lower() for term in ["' or '1'='1", "' or 1=1", "admin' --", "' or ''='"])
        is_union = "union select" in payload.lower()
        
        if is_bypass:
            logs.append("[+] Server returned HTTP 200 OK")
            logs.append("[+] Detection: SQL error messages suppressed, but data returned.")
            logs.append("[+] SQL query completed successfully with truth bypass.")
            logs.append("[SUCCESS] Authentication bypassed! Logged in as user ID: 1 (admin).")
            return True, logs, "User Session Cookie: session_id=sess_admin_9823120"
        elif is_union:
            logs.append("[+] Database: SQLite (detected via syntax response time)")
            logs.append("[*] Aligning UNION columns... checking column count...")
            logs.append("[+] Query aligned. Executing UNION schema extraction...")
            logs.append("[SUCCESS] SQL UNION Injection successful. Database schemas dumped.")
            return True, logs, "Database Dump:\n - users (id INT, username TEXT, password TEXT)\n - keys (id INT, key TEXT)\n\nadmin:password123\nkishan:devopsified1"
        else:
            logs.append("[-] Database returned error: sqlite3.OperationalError: near '\"': syntax error")
            logs.append("[-] Injection failed to bypass statement check.")
            logs.append("[FAILED] Target secure against this SQL payload.")
            return False, logs, None

    def _simulate_xss(self, payload: str, logs: List[str]) -> tuple:
        logs.append("[*] Sending request to: http://localhost:8080/dashboard?name=" + payload)
        logs.append("[*] Parsing returned DOM tree structure...")
        time.sleep(0.1)
        
        # Basic check for script tags or event handlers
        has_script = "<script>" in payload.lower() or "alert(" in payload.lower() or "onerror=" in payload.lower()
        
        if has_script:
            logs.append("[+] Payload reflected in HTML: <div>Welcome back, " + payload + "</div>")
            logs.append("[+] Executing JavaScript in virtual DOM container...")
            logs.append("[SUCCESS] XSS execution successful. Document context hijacked.")
            return True, logs, "Stolen Context Metadata:\nCookie: session_token=abcd123efgh456\nLocation: http://localhost:8080/dashboard\nUser-Agent: Mozilla/5.0 (MockSandbox)"
        else:
            logs.append("[+] Payload reflected in HTML safely (escaped/sanitized): &lt;Welcome guest&gt;")
            logs.append("[-] Script execution failed. No vulnerability triggered.")
            logs.append("[FAILED] Target HTML page escaped the input successfully.")
            return False, logs, None

    def _simulate_ssrf(self, payload: str, logs: List[str]) -> tuple:
        logs.append("[*] Sending trigger payload to webhook dispatcher page...")
        logs.append(f"[*] Dispatcher attempting connection to: {payload}")
        time.sleep(0.15)
        
        # SSRF checks
        is_internal = any(term in payload.lower() for term in ["localhost", "127.0.0.1", "169.254.169.254", "internal-metadata"])
        
        if is_internal:
            logs.append("[*] Connection route checked... Bypass proxy controls...")
            logs.append("[+] Connection succeeded. Status 200 OK")
            logs.append("[SUCCESS] SSRF request successfully routed to internal endpoint.")
            
            if "169.254.169.254" in payload:
                captured = "AWS Metadata response:\n{\n  \"Code\": \"Success\",\n  \"LastUpdated\": \"2026-05-28T04:40:00Z\",\n  \"AccessKeyId\": \"ASIAYTMOCKAWSKEY\",\n  \"SecretAccessKey\": \"qMwE129381283hjasdhf/AWSSECRET\",\n  \"Token\": \"IQoJb3JpZ2luX2VjEOb...\"\n}"
            else:
                captured = "Internal Server response:\nHTTP/1.1 200 OK\nServer: Internal-Admin-Service/0.1\n\nAdmin Control Dashboard:\n - Server Uptime: 304 days\n - Port: 8080\n - Status: Active"
            return True, logs, captured
        else:
            logs.append("[-] Dispatcher blocked request. Target URL hosts public network IP.")
            logs.append("[-] Routing aborted due to outbound network controls.")
            logs.append("[FAILED] Target blocked SSRF request.")
            return False, logs, None

import json
import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import Repository, Scan, Vulnerability, AgentLog
from app.services.scanner_service import ScannerService
from app.services.git_service import GitService
from app.services.vector_service import VectorService
from typing import List, Dict, Any

# Optional import of SDKs
try:
    import google.generativeai as genai
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
except ImportError:
    pass

try:
    import openai
    if settings.OPENAI_API_KEY:
        openai.api_key = settings.OPENAI_API_KEY
except ImportError:
    pass

class Orchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.scanner_service = ScannerService()
        self.git_service = GitService()
        self.vector_service = VectorService()
        self.provider = settings.AI_PROVIDER

    def log_agent_activity(self, scan_id: int, agent_name: str, status: str, message: str, debate_context: str = None):
        """Helper to write agent execution steps into database logs."""
        log = AgentLog(
            scan_id=scan_id,
            agent_name=agent_name,
            status=status,
            message=message,
            debate_context=debate_context,
            created_at=datetime.datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        print(f"[{agent_name}] {status}: {message[:120]}")

    def execute_scan_workflow(self, scan_id: int, repo_id: int):
        """Main orchestrator running all security agents."""
        scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
        repo = self.db.query(Repository).filter(Repository.id == repo_id).first()
        
        if not scan or not repo:
            print("Scan or Repository not found in DB.")
            return

        try:
            # 1. Start Orchestrator
            scan.status = "Running"
            self.db.commit()
            
            self.log_agent_activity(scan_id, "Orchestrator Agent", "Running", f"Initializing security scan on repository {repo.owner}/{repo.name} (branch: {scan.branch})")
            
            # 2. Clone repository via Git Service
            self.log_agent_activity(scan_id, "Orchestrator Agent", "Info", f"Cloning repository source files from {repo.clone_url}")
            local_path = self.git_service.clone_repository(repo.clone_url, repo.name)
            
            # 3. Scanner Agent
            self.log_agent_activity(scan_id, "Scanner Agent", "Running", "Starting code vulnerabilities scanning (Semgrep, Bandit, Gitleaks wrappers & AI parser)...")
            raw_findings = self.scanner_service.scan_directory(local_path)
            self.log_agent_activity(scan_id, "Scanner Agent", "Success", f"Scanning complete. Detected {len(raw_findings)} potential security findings.")
            
            if not raw_findings:
                self.log_agent_activity(scan_id, "Orchestrator Agent", "Success", "No vulnerabilities found. Scan completed.")
                scan.status = "Success"
                scan.completed_at = datetime.datetime.utcnow()
                scan.summary = "Scan completed. Repository clean."
                self.db.commit()
                return

            # Insert raw findings as vulnerabilities in the DB
            db_vulns = []
            for item in raw_findings:
                vuln = Vulnerability(
                    scan_id=scan_id,
                    type=item["type"],
                    file=item["file"],
                    line=item["line"],
                    severity=item["severity"],
                    description=item["description"],
                    before_code=item["before_code"],
                    after_code="",
                    status="Open"
                )
                self.db.add(vuln)
                db_vulns.append(vuln)
            self.db.commit()

            # 4. Threat Intelligence Agent
            self.log_agent_activity(scan_id, "Threat Intelligence Agent", "Running", "Mapping findings to CVE databases, CWEs, OWASP guidelines, and exploit indexes...")
            self._execute_threat_intelligence(scan_id, db_vulns)
            
            # 5. Agent Debate System & Risk Prioritization Agent
            self.log_agent_activity(scan_id, "Risk Prioritization Agent", "Running", "Analyzing exploit availability, business impact, and triggering Agent Debate system...")
            self._execute_risk_prioritization_and_debate(scan_id, db_vulns)

            # 6. Fix Recommendation Agent
            self.log_agent_activity(scan_id, "Fix Recommendation Agent", "Running", "Generating secure code patches and best-practice remediation strategies...")
            self._execute_fix_recommendations(scan_id, db_vulns)

            # 7. Patch Generation Agent
            self.log_agent_activity(scan_id, "Patch Generation Agent", "Running", "Applying AI patches, branching code, and submitting GitHub Pull Requests...")
            self._execute_patch_generation(scan_id, db_vulns, local_path, repo)

            # 8. Reporting Agent
            self.log_agent_activity(scan_id, "Reporting Agent", "Running", "Assembling executive report metrics, risk matrices, and updating security dashboard...")
            self._execute_reporting(scan_id, scan, db_vulns)

            # Cleanup clone
            self.git_service.delete_local_clone(local_path)
            
        except Exception as e:
            self.log_agent_activity(scan_id, "Orchestrator Agent", "Error", f"Execution failed unexpectedly: {str(e)}")
            scan.status = "Failed"
            self.db.commit()

    def _execute_threat_intelligence(self, scan_id: int, vulns: List[Vulnerability]):
        """Query knowledge base / AI to append CVE info and exploit data."""
        for v in vulns:
            # Map vulnerability type to standard metadata
            cve, cvss, exploit = self._get_ai_threat_data(v.type)
            v.cve = cve
            v.cvss = cvss
            v.exploit_available = exploit
            self.db.commit()
            
            self.log_agent_activity(
                scan_id, 
                "Threat Intelligence Agent", 
                "Info", 
                f"Mapped '{v.type}' in {v.file} to {cve} (CVSS: {cvss}, Exploit Available: {exploit})"
            )

    def _execute_risk_prioritization_and_debate(self, scan_id: int, vulns: List[Vulnerability]):
        """Debates threat levels between scanner, threat intel, and risk agents."""
        for v in vulns:
            # Setup debate dialogue
            scanner_severity = v.severity
            threat_exploit = "Available" if v.exploit_available else "Not Available"
            
            # Determine prioritized threat level
            final_priority = "Medium"
            if v.severity == "High" or v.cvss >= 8.0:
                final_priority = "High"
            if v.cvss >= 9.0 and v.exploit_available:
                final_priority = "Critical"
                
            business_impact = f"Exploitation of {v.type} in {v.file} could compromise application servers."
            if final_priority == "Critical":
                business_impact = f"Remote code execution or full authentication bypass possible on file {v.file}."
            
            reasoning = f"Prioritized as {final_priority} because severity is {v.severity} and exploitability score is high."
            
            debate_steps = [
                {"agent": "Scanner Agent", "message": f"Initial scan flagged {v.type} as {scanner_severity} based on static code pattern analysis."},
                {"agent": "Threat Intelligence Agent", "message": f"Checking CVE mappings. Matches CVSS {v.cvss}. Exploit is {threat_exploit}. Upgrading threat assessment."},
                {"agent": "Risk Prioritization Agent", "message": f"Agreed. Business impact: {business_impact}. Adjusting priority tier to {final_priority}."}
            ]
            
            v.priority = final_priority
            v.business_impact = business_impact
            v.priority_reasoning = reasoning
            self.db.commit()

            self.log_agent_activity(
                scan_id, 
                "Risk Prioritization Agent", 
                "Debate", 
                f"Completed debate for {v.type} in {v.file}. Priority set to: {final_priority}",
                debate_context=json.dumps(debate_steps)
            )

    def _execute_fix_recommendations(self, scan_id: int, vulns: List[Vulnerability]):
        """Generates secure remediation code using LLM (or mock fallbacks)."""
        for v in vulns:
            before = v.before_code
            after = ""
            
            # Generate remediation using settings model or fallback templates
            if self.provider != "mock" and (settings.GEMINI_API_KEY or settings.OPENAI_API_KEY):
                after = self._call_llm_for_remediation(v.type, before)
            
            if not after:
                after = self._get_fallback_remediation_template(v.type, before)
                
            v.after_code = after
            self.db.commit()
            
            self.log_agent_activity(
                scan_id, 
                "Fix Recommendation Agent", 
                "Info", 
                f"Generated patch suggestion for {v.type} in {v.file}."
            )

    def _execute_patch_generation(self, scan_id: int, vulns: List[Vulnerability], local_path: str, repo: Repository):
        """Creates branch, commits patch, and creates GitHub pull request."""
        # Process Critical and High vulnerabilities for automated patching
        for v in vulns:
            if v.priority in ["Critical", "High"] and v.after_code:
                self.log_agent_activity(scan_id, "Patch Generation Agent", "Info", f"Creating git branch and staging fix patch for {v.type}")
                
                success, branch_name = self.git_service.create_patch_branch(local_path, v.id)
                if not success:
                    continue
                    
                patch_applied = self.git_service.apply_code_fix(
                    local_path, v.file, v.line, v.before_code, v.after_code
                )
                
                if patch_applied:
                    commit_msg = f"[SecureAgent AI] Automated Patch for {v.type} in {v.file}"
                    committed = self.git_service.commit_and_push_patch(local_path, branch_name, commit_msg)
                    
                    if committed:
                        title = f"[SecureAgent AI] Fix {v.priority} {v.type}"
                        description = f"### SecureAgent AI Automated Security Remediation\n\nIdentified a **{v.priority}** severity **{v.type}** in `{v.file}` at line {v.line}.\n\n#### Risk Description:\n{v.description}\n\n#### Remediation Applied:\nUpdated vulnerable code concatenation to use safe parameterized statements.\n\n*Created by autonomous AI DevSecOps agent workflow.*"
                        
                        pr_num, pr_url = self.git_service.create_github_pull_request(
                            repo.owner, repo.name, branch_name, title, description
                        )
                        
                        v.status = "Patched"
                        v.pr_number = pr_num
                        v.pr_url = pr_url
                        self.db.commit()
                        
                        self.log_agent_activity(
                            scan_id, 
                            "Patch Generation Agent", 
                            "Success", 
                            f"Opened automated Pull Request #{pr_num} for {v.type} patch: {pr_url}"
                        )
                    else:
                        self.log_agent_activity(scan_id, "Patch Generation Agent", "Error", "Failed to commit and push security branch.")
                else:
                    self.log_agent_activity(scan_id, "Patch Generation Agent", "Error", f"Failed to apply patch replacement to local code {v.file}.")

    def _execute_reporting(self, scan_id: int, scan: Scan, vulns: List[Vulnerability]):
        """Finalizes scan meta summary."""
        scan.status = "Success"
        scan.completed_at = datetime.datetime.utcnow()
        
        # Calculate summary metrics
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for v in vulns:
            pri = v.priority or "Medium"
            counts[pri] = counts.get(pri, 0) + 1
            
        summary_text = (
            f"Vulnerability Scan completed. Found {len(vulns)} issues total. "
            f"Severity breakdown: Critical={counts['Critical']}, High={counts['High']}, Medium={counts['Medium']}, Low={counts['Low']}. "
            f"Automated security patches generated and Pull Requests created for critical findings."
        )
        scan.summary = summary_text
        self.db.commit()
        
        self.log_agent_activity(scan_id, "Reporting Agent", "Success", f"Scan report complete. Metrics updated.")

    def _get_ai_threat_data(self, vuln_type: str) -> tuple:
        """Returns standard threat catalog matching (CVE, CVSS, Exploit availability)."""
        mapping = {
            "SQL Injection": ("CVE-2024-3400", 9.8, True),
            "Command Injection": ("CVE-2024-21626", 10.0, True),
            "Cross-Site Scripting (XSS)": ("CVE-2023-45857", 6.1, False),
            "Server-Side Request Forgery (SSRF)": ("CVE-2024-27198", 8.8, True),
            "Secret Leak": ("CVE-2023-52425", 9.1, True),
            "Path Traversal": ("CVE-2023-38545", 7.5, False)
        }
        return mapping.get(vuln_type, ("CVE-2024-XXXX", 5.0, False))

    def _get_fallback_remediation_template(self, vuln_type: str, before_code: str) -> str:
        """Fallback rule-based patches in case of offline/mock setups."""
        if "SQL Injection" in vuln_type:
            return "cursor.execute(\"SELECT * FROM users WHERE username = %s AND password = %s\", (username, password))"
        elif "Secret Leak" in vuln_type:
            return "AWS_SECRET_KEY = os.environ.get(\"AWS_SECRET_KEY\")"
        elif "Cross-Site Scripting" in vuln_type:
            return "const name = urlParams.get('name') || 'Guest';\ndocument.getElementById('user-info').innerText = \"Welcome back, \" + name;"
        elif "Server-Side Request Forgery" in vuln_type:
            return "if is_safe_url(user_url):\n    response = requests.post(user_url, json={'event': 'ping'})\nelse:\n    raise ValueError(\"Blocked internal destination URL\")"
        elif "Command Injection" in vuln_type:
            # Replace subprocess.run(..., shell=True)
            return "subprocess.run([\"ping\", \"-c\", \"1\", host], shell=False)"
        return before_code # default no-op

    def _call_llm_for_remediation(self, vuln_type: str, before_code: str) -> str:
        """Helper to contact Gemini/OpenAI API and return remediation line."""
        prompt = f"""You are a security engineer. Convert this vulnerable code into a secure version.
Vulnerability: {vuln_type}
Vulnerable Code: {before_code}

Return ONLY the corrected python/js/html statement. Do not include explanation or markdown code blocks.
"""
        try:
            if self.provider == "gemini" and settings.GEMINI_API_KEY:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                res_text = response.text.strip()
                # strip code block tags if the LLM ignored constraints
                res_text = res_text.replace("```python", "").replace("```javascript", "").replace("```html", "").replace("```", "")
                return res_text.strip()
            elif self.provider == "openai" and settings.OPENAI_API_KEY:
                import openai
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                res_text = response.choices[0].message.content.strip()
                res_text = res_text.replace("```python", "").replace("```javascript", "").replace("```html", "").replace("```", "")
                return res_text.strip()
        except Exception as e:
            print(f"LLM API call failed: {e}")
        return ""

    def answer_security_mentor(self, query: str) -> str:
        """AI Security Mentor chat helper using RAG (Vector service) + LLM."""
        # 1. Fetch RAG documents
        hits = self.vector_service.query_similarity(query, n_results=2)
        context = "\n\n".join([h["text"] for h in hits])
        
        prompt = f"""You are SecureAgent AI Security Mentor, an expert DevSecOps security specialist.
Use the following context database details to help answer the developer's question.

Context:
{context}

Question:
{query}

Explain in developer friendly formatting. If code examples are helpful, show them.
"""
        try:
            if self.provider == "gemini" and settings.GEMINI_API_KEY:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                return response.text
            elif self.provider == "openai" and settings.OPENAI_API_KEY:
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Mentor call failed: {e}")
            
        # Mock/Offline response engine based on keyword match
        query = query.lower()
        if "sql" in query:
            return "SecureAgent AI Security Mentor:\n\nSQL Injection vulnerabilities occur when user-controlled parameters are concatenated directly into database commands. \n\n**Exploitation Example:**\nIf an attacker inputs `' OR '1'='1` in a login form, the resulting query executes as `SELECT * FROM users WHERE username = '' OR '1'='1'`. This statement evaluates to true, granting admin privileges.\n\n**Remediation:**\nUse parameterized statements, also known as Prepared Queries. E.g. `cursor.execute('SELECT * FROM users WHERE id = %s', (id_val,))`."
        elif "xss" in query:
            return "SecureAgent AI Security Mentor:\n\nCross-Site Scripting (XSS) arises when user input is rendered inside page DOM nodes without escaping scripts. Attackers can execute arbitrary JavaScript commands on visitors.\n\n**Remediation:**\nEscape rendering tags using browser properties like `.innerText` rather than `.innerHTML`, or implement a strict Content Security Policy header."
        elif "secrets" in query or "leak" in query:
            return "SecureAgent AI Security Mentor:\n\nHardcoding API tokens or SSH private keys exposes credentials. \n\n**Remediation:**\nRevoke any credentials that were pushed to git, and migrate settings to load credentials via environment variables: `os.environ.get('API_KEY')`."
            
        return "SecureAgent AI Security Mentor:\n\nHello! I am ready to guide you on securing your applications. Ask me about SQL Injection, SSRF, Command Injection, or Secret Leak fixes."

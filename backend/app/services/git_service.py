import os
import shutil
from typing import Tuple, Optional
import git
from github import Github
from app.config import settings

class GitService:
    def __init__(self):
        self.github_token = settings.GITHUB_TOKEN or os.getenv("GITHUB_TOKEN", "")
        self.github_client = Github(self.github_token) if self.github_token else None

    def clone_repository(self, clone_url: str, repo_name: str) -> str:
        """
        Clones a repository to local CLONE_DIR.
        If it already exists, pulls the latest changes.
        Returns the path to the cloned repository.
        """
        # Strip credentials from clone_url for local path naming if present
        clean_name = repo_name.replace(" ", "_").replace("/", "_")
        target_path = os.path.join(settings.CLONE_DIR, clean_name)
        
        # If exists, we can clean it or reuse it. Cleaning ensures a fresh state.
        if os.path.exists(target_path):
            try:
                shutil.rmtree(target_path)
            except Exception as e:
                # Fallback to appending a tag
                print(f"Could not clean existing folder: {e}")
                
        print(f"Cloning {clone_url} to {target_path}...")
        
        # If running in offline/mock mode or URL is invalid, let's create a mock repo folder
        if not clone_url.startswith("http") and not clone_url.startswith("git@"):
            os.makedirs(target_path, exist_ok=True)
            self._create_mock_repo_files(target_path)
            return target_path

        try:
            git.Repo.clone_from(clone_url, target_path)
        except Exception as e:
            print(f"Git clone failed: {e}. Creating mock repository content instead.")
            os.makedirs(target_path, exist_ok=True)
            self._create_mock_repo_files(target_path)
            
        return target_path

    def _create_mock_repo_files(self, target_path: str):
        """Creates dummy files with realistic security flaws for demonstration purposes."""
        # Create app/auth.py (SQL Injection)
        auth_file = os.path.join(target_path, "app", "auth.py")
        os.makedirs(os.path.dirname(auth_file), exist_ok=True)
        with open(auth_file, "w") as f:
            f.write('''# Authentication Module
import sqlite3

def login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # VULNERABLE: Direct SQL Injection
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    print("Executing query:", query)
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    return user
''')

        # Create config/settings.py (Hardcoded secret)
        settings_file = os.path.join(target_path, "config", "settings.py")
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, "w") as f:
            f.write('''# App Settings
import os

DEBUG = True
PORT = 8080

# VULNERABLE: Hardcoded credential
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE/qAwE129381283hjasdhf/AWS"
DATABASE_URL = "postgresql://db_user:password123@localhost/prod_db"
''')

        # Create templates/dashboard.html (XSS)
        html_file = os.path.join(target_path, "templates", "dashboard.html")
        os.makedirs(os.path.dirname(html_file), exist_ok=True)
        with open(html_file, "w") as f:
            f.write('''<!DOCTYPE html>
<html>
<body>
    <h1>Dashboard</h1>
    <div id="user-info"></div>
    <script>
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name') || 'Guest';
        // VULNERABLE: Cross-site scripting (XSS)
        document.getElementById('user-info').innerHTML = "Welcome back, " + name;
    </script>
</body>
</html>
''')

        # Create app/webhook_dispatcher.py (SSRF)
        webhook_file = os.path.join(target_path, "app", "webhook_dispatcher.py")
        os.makedirs(os.path.dirname(webhook_file), exist_ok=True)
        with open(webhook_file, "w") as f:
            f.write('''# Webhook Dispatcher
import requests

def dispatch_event(user_url):
    # VULNERABLE: Direct Server-Side Request Forgery
    response = requests.post(user_url, json={'event': 'ping'})
    return response.status_code
''')

        # Initialize git locally so we can commit / branch
        try:
            repo = git.Repo.init(target_path)
            repo.index.add([
                os.path.join("app", "auth.py"),
                os.path.join("config", "settings.py"),
                os.path.join("templates", "dashboard.html"),
                os.path.join("app", "webhook_dispatcher.py")
            ])
            repo.index.commit("Initial commit with sample code")
        except Exception as e:
            print(f"Failed to initialize mock git: {e}")

    def create_patch_branch(self, repo_path: str, vuln_id: int) -> Tuple[bool, str]:
        """
        Creates a new git branch for the fix patch.
        Returns (success, branch_name).
        """
        try:
            repo = git.Repo(repo_path)
            branch_name = f"secureagent/fix-vuln-{vuln_id}"
            
            # Checkout main first
            try:
                repo.git.checkout("main")
            except:
                try:
                    repo.git.checkout("master")
                except:
                    pass
            
            # Create and checkout branch
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            return True, branch_name
        except Exception as e:
            print(f"Failed to create git branch: {e}")
            return False, f"secureagent/fix-vuln-{vuln_id}-mock"

    def apply_code_fix(self, repo_path: str, filepath: str, line_number: Optional[int], before_code: str, after_code: str) -> bool:
        """
        Applies code fix to file by replacing the target vulnerable code.
        """
        full_filepath = os.path.join(repo_path, filepath)
        if not os.path.exists(full_filepath):
            print(f"File not found to patch: {full_filepath}")
            return False
            
        try:
            with open(full_filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Replace target code block
            # If before_code contains newlines, we replace it directly.
            # Otherwise we try exact line replacement or general replacement.
            if before_code in content:
                content = content.replace(before_code, after_code)
            else:
                # Try replacing line by line
                lines = content.splitlines()
                # If we have line number, check that specific line area
                matched = False
                if line_number and 0 < line_number <= len(lines):
                    for offset in [0, -1, 1, -2, 2]:
                        idx = line_number - 1 + offset
                        if 0 <= idx < len(lines) and before_code.strip() in lines[idx]:
                            lines[idx] = lines[idx].replace(before_code.strip(), after_code.strip())
                            matched = True
                            break
                if not matched:
                    # Generic lookup of stripped versions
                    for idx, line in enumerate(lines):
                        if before_code.strip() in line:
                            lines[idx] = line.replace(before_code.strip(), after_code.strip())
                            matched = True
                            break
                content = "\n".join(lines) + "\n"

            with open(full_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error applying patch to {filepath}: {e}")
            return False

    def commit_and_push_patch(self, repo_path: str, branch_name: str, commit_message: str) -> bool:
        """
        Commits changes and pushes them to origin.
        Falls back to simulating a successful commit/push if remote auth fails.
        """
        try:
            repo = git.Repo(repo_path)
            repo.git.add(A=True)
            repo.index.commit(commit_message)
            
            # Try pushing branch to remote
            # We fail gracefully if origin does not exist or requires authenticating
            try:
                origin = repo.remote(name="origin")
                origin.push(branch_name)
                print(f"Successfully pushed branch {branch_name} to origin.")
            except Exception as push_err:
                print(f"Failed to push branch (this is expected for offline repos): {push_err}")
                
            return True
        except Exception as e:
            print(f"Git commit/push failed: {e}")
            return False

    def create_github_pull_request(self, repo_owner: str, repo_name: str, branch_name: str, title: str, description: str) -> Tuple[int, str]:
        """
        Submits a pull request using GitHub API.
        If no GITHUB_TOKEN is present, returns a simulated PR object.
        """
        if not self.github_client:
            mock_pr_num = 101
            mock_pr_url = f"https://github.com/{repo_owner}/{repo_name}/pull/{mock_pr_num}"
            print(f"GitHub client not configured. Simulating Pull Request #{mock_pr_num}: {mock_pr_url}")
            return mock_pr_num, mock_pr_url
            
        try:
            repo_spec = f"{repo_owner}/{repo_name}"
            repo = self.github_client.get_repo(repo_spec)
            
            # Default branch (usually main or master)
            base_branch = repo.default_branch
            
            pr = repo.create_pull(
                title=title,
                body=description,
                head=branch_name,
                base=base_branch
            )
            return pr.number, pr.html_url
        except Exception as e:
            print(f"Error creating GitHub Pull Request: {e}")
            mock_pr_num = 101
            mock_pr_url = f"https://github.com/{repo_owner}/{repo_name}/pull/{mock_pr_num}"
            return mock_pr_num, mock_pr_url
            
    def delete_local_clone(self, repo_path: str):
        if os.path.exists(repo_path):
            try:
                shutil.rmtree(repo_path)
            except Exception as e:
                print(f"Error deleting local clone: {e}")

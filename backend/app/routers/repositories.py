import re
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Repository, Scan
from app.schemas import RepositoryCreate, RepositoryResponse, WebhookPayload
from app.agents.orchestrator import Orchestrator
from typing import List

router = APIRouter()

def parse_github_url(url: str):
    """Extracts owner and name from a GitHub clone url."""
    # Match SSH or HTTPS
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)", url)
    if match:
        return match.group(1), match.group(2)
    # Default fallback
    return "local", "demo-repo"

@router.post("/repositories", response_model=RepositoryResponse)
def create_repository(repo_in: RepositoryCreate, db: Session = Depends(get_db)):
    owner, name = parse_github_url(repo_in.clone_url)
    
    # Check if duplicate
    existing = db.query(Repository).filter(Repository.clone_url == repo_in.clone_url).first()
    if existing:
        return existing
        
    db_repo = Repository(
        owner=owner,
        name=name,
        clone_url=repo_in.clone_url,
        branch=repo_in.branch or "main",
        status="Idle"
    )
    db.add(db_repo)
    db.commit()
    db.refresh(db_repo)
    return db_repo

@router.get("/repositories", response_model=List[RepositoryResponse])
def get_repositories(db: Session = Depends(get_db)):
    return db.query(Repository).all()

@router.get("/repositories/{repo_id}", response_model=RepositoryResponse)
def get_repository_detail(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo

@router.delete("/repositories/{repo_id}")
def delete_repository(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    db.delete(repo)
    db.commit()
    return {"message": "Repository deleted successfully"}

# 1. GitHub Webhook Integration
@router.post("/webhooks/github")
def github_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Receives GitHub repository Push webhooks.
    Identifies the repo, registers the scan, and initiates the multi-agent orchestration pipeline.
    """
    repo_data = payload.repository
    clone_url = repo_data.get("clone_url")
    ref = payload.ref
    branch = ref.split("/")[-1] if "/" in ref else "main"
    
    # Locate or register repository in database
    owner = repo_data.get("owner", {}).get("name", "github")
    name = repo_data.get("name")
    
    db_repo = db.query(Repository).filter(Repository.clone_url == clone_url).first()
    if not db_repo:
        db_repo = Repository(
            owner=owner,
            name=name,
            clone_url=clone_url,
            branch=branch,
            status="Idle"
        )
        db.add(db_repo)
        db.commit()
        db.refresh(db_repo)

    # Initialize a new scan execution record
    scan = Scan(
        repository_id=db_repo.id,
        status="Pending",
        branch=branch,
        commit_sha=payload.after or "head"
    )
    db.add(scan)
    db_repo.status = "Scanning"
    db.commit()
    db.refresh(scan)
    
    # Run Orchestrator workflow asynchronously in background task thread
    orchestrator = Orchestrator(db)
    background_tasks.add_task(orchestrator.execute_scan_workflow, scan.id, db_repo.id)
    
    return {
        "status": "Webhook acknowledged. Scan scheduled.",
        "scan_id": scan.id,
        "repository": f"{owner}/{name}"
    }

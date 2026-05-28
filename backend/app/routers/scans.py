from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Scan, Repository, AgentLog
from app.schemas import ScanResponse, AgentLogResponse
from app.agents.orchestrator import Orchestrator
from typing import List

router = APIRouter()

@router.post("/scans/trigger/{repo_id}", response_model=ScanResponse)
def trigger_scan(repo_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers a scan manually for a registered repository."""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    if repo.status == "Scanning":
        raise HTTPException(status_code=400, detail="Repository is already undergoing a scan.")
        
    scan = Scan(
        repository_id=repo.id,
        status="Pending",
        branch=repo.branch or "main",
        commit_sha="manual-run"
    )
    db.add(scan)
    repo.status = "Scanning"
    db.commit()
    db.refresh(scan)
    
    # Fire off orchestrator agent background job
    orchestrator = Orchestrator(db)
    background_tasks.add_task(orchestrator.execute_scan_workflow, scan.id, repo.id)
    
    return scan

@router.get("/scans", response_model=List[ScanResponse])
def get_scans(db: Session = Depends(get_db)):
    return db.query(Scan).order_by(Scan.created_at.desc()).all()

@router.get("/scans/repo/{repo_id}", response_model=List[ScanResponse])
def get_scans_by_repo(repo_id: int, db: Session = Depends(get_db)):
    return db.query(Scan).filter(Scan.repository_id == repo_id).order_by(Scan.created_at.desc()).all()

@router.get("/scans/{scan_id}", response_model=ScanResponse)
def get_scan_detail(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/scans/{scan_id}/logs", response_model=List[AgentLogResponse])
def get_scan_agent_logs(scan_id: int, db: Session = Depends(get_db)):
    """Returns sequential progress logs of AI Agents execution."""
    logs = db.query(AgentLog).filter(AgentLog.scan_id == scan_id).order_by(AgentLog.created_at.asc()).all()
    return logs

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Vulnerability, Scan, ChatHistory
from app.schemas import (
    VulnerabilityResponse, 
    VulnerabilityUpdateStatus, 
    SimulationRequest, 
    SimulationResponse,
    ChatMessageResponse,
    ChatMessageCreate
)
from app.services.attack_simulation import AttackSimulator
from app.agents.orchestrator import Orchestrator
from typing import List

router = APIRouter()
simulator = AttackSimulator()

@router.get("/vulnerabilities", response_model=List[VulnerabilityResponse])
def get_all_vulnerabilities(db: Session = Depends(get_db)):
    return db.query(Vulnerability).order_by(Vulnerability.cvss.desc()).all()

@router.get("/vulnerabilities/scan/{scan_id}", response_model=List[VulnerabilityResponse])
def get_vulnerabilities_by_scan(scan_id: int, db: Session = Depends(get_db)):
    return db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).all()

@router.get("/vulnerabilities/{vuln_id}", response_model=VulnerabilityResponse)
def get_vulnerability_detail(vuln_id: int, db: Session = Depends(get_db)):
    vuln = db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln

@router.put("/vulnerabilities/{vuln_id}/status", response_model=VulnerabilityResponse)
def update_vulnerability_status(vuln_id: int, status_update: VulnerabilityUpdateStatus, db: Session = Depends(get_db)):
    vuln = db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    vuln.status = status_update.status
    db.commit()
    db.refresh(vuln)
    return vuln

# 2. Attack Simulation Endpoint
@router.post("/simulate", response_model=SimulationResponse)
def run_simulation(req: SimulationRequest):
    """Executes safe sandboxed mock exploits to check vulnerability severity."""
    res = simulator.simulate_exploit(req)
    return res

# 3. AI Security Mentor Chatbot
@router.post("/mentor/chat", response_model=ChatMessageResponse)
def chat_with_mentor(chat_in: ChatMessageCreate, db: Session = Depends(get_db)):
    # Save User message
    user_msg = ChatHistory(message=chat_in.message, sender="user")
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    
    # Query AI Security Mentor RAG system
    orchestrator = Orchestrator(db)
    response_text = orchestrator.answer_security_mentor(chat_in.message)
    
    # Save AI Mentor response
    mentor_msg = ChatHistory(message=response_text, sender="mentor")
    db.add(mentor_msg)
    db.commit()
    db.refresh(mentor_msg)
    
    return mentor_msg

@router.get("/mentor/history", response_model=List[ChatMessageResponse])
def get_chat_history(db: Session = Depends(get_db)):
    return db.query(ChatHistory).order_by(ChatHistory.timestamp.asc()).all()

@router.post("/mentor/clear")
def clear_chat_history(db: Session = Depends(get_db)):
    db.query(ChatHistory).delete()
    db.commit()
    return {"message": "Chat history cleared"}

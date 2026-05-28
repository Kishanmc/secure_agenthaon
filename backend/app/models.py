import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String, index=True)
    name = Column(String, index=True)
    clone_url = Column(String)
    branch = Column(String, default="main")
    status = Column(String, default="Idle")  # Idle, Scanning, Scanned, Failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    scans = relationship("Scan", back_populates="repository", cascade="all, delete-orphan")

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"))
    status = Column(String, default="Pending")  # Pending, Running, Success, Failed
    branch = Column(String)
    commit_sha = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    repository = relationship("Repository", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLog", back_populates="scan", cascade="all, delete-orphan")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"))
    type = Column(String, index=True)  # SQL Injection, XSS, SSRF, Command Injection, Secrets Leak, etc.
    file = Column(String, index=True)
    line = Column(Integer, nullable=True)
    severity = Column(String)  # Critical, High, Medium, Low (Initial from scanner)
    
    # Threat Intel & Risk Prioritization fields
    cve = Column(String, nullable=True)
    cvss = Column(Float, nullable=True)
    exploit_available = Column(Boolean, default=False)
    priority = Column(String, nullable=True)  # Critical, High, Medium, Low (Prioritized)
    business_impact = Column(Text, nullable=True)
    priority_reasoning = Column(Text, nullable=True)
    
    # Fix and remediation
    description = Column(Text)
    before_code = Column(Text)
    after_code = Column(Text)
    
    # Patch and PR status
    status = Column(String, default="Open")  # Open, Patching, Patched, Ignored
    pr_number = Column(Integer, nullable=True)
    pr_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    scan = relationship("Scan", back_populates="vulnerabilities")

class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"))
    agent_name = Column(String)  # Orchestrator, Scanner, ThreatIntel, RiskPrioritization, FixRecommendation, PatchGenerator, Reporter
    status = Column(String)  # Info, Debate, Running, Success, Error
    message = Column(Text)
    debate_context = Column(Text, nullable=True)  # JSON representation of debates or chat transcripts
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    scan = relationship("Scan", back_populates="agent_logs")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    sender = Column(String)  # user, mentor
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

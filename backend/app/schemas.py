from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

# Repository Schemas
class RepositoryBase(BaseModel):
    owner: str
    name: str
    clone_url: str
    branch: Optional[str] = "main"

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryResponse(RepositoryBase):
    id: int
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Scan Schemas
class ScanBase(BaseModel):
    repository_id: int
    branch: Optional[str] = "main"

class ScanCreate(ScanBase):
    pass

class ScanResponse(BaseModel):
    id: int
    repository_id: int
    status: str
    branch: str
    commit_sha: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

# Vulnerability Schemas
class VulnerabilityBase(BaseModel):
    type: str
    file: str
    line: Optional[int] = None
    severity: str
    cve: Optional[str] = None
    cvss: Optional[float] = None
    exploit_available: bool = False
    priority: Optional[str] = None
    business_impact: Optional[str] = None
    priority_reasoning: Optional[str] = None
    description: str
    before_code: str
    after_code: str
    status: str
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None

class VulnerabilityResponse(VulnerabilityBase):
    id: int
    scan_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class VulnerabilityUpdateStatus(BaseModel):
    status: str

# Agent Log Schemas
class AgentLogBase(BaseModel):
    agent_name: str
    status: str
    message: str
    debate_context: Optional[str] = None

class AgentLogResponse(AgentLogBase):
    id: int
    scan_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessageBase(BaseModel):
    message: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    sender: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

# Simulation Schema
class SimulationRequest(BaseModel):
    vulnerability_type: str = Field(description="SQL Injection, XSS, or SSRF")
    payload: str
    target_url: Optional[str] = None

class SimulationResponse(BaseModel):
    success: bool
    vulnerability_type: str
    payload: str
    execution_logs: List[str]
    captured_data: Optional[str] = None
    remediation_blocked: bool = False

# Mock Webhook Trigger
class WebhookPayload(BaseModel):
    repository: dict
    ref: str
    after: Optional[str] = None

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

# ===== EXISTING MODELS (KEEP THESE) =====

class IncidentLog(BaseModel):
    pid: int
    timestamp: float
    action: str
    command_line: str
    user: str = None
    forensic_path: str = None
    details: Dict[str, Any] = {}

class BaselineEntry(BaseModel):
    exec_path: str
    user: str
    fingerprint: str

class Baseline(BaseModel):
    entries: List[BaselineEntry] = []

class Policy(BaseModel):
    allow: List[str]
    block: List[str]

class AgentInfo(BaseModel):
    pid: int
    start_time: float
    hostname: str

class Evidence(BaseModel):
    id: str
    type: str
    created: float
    summary: str
    file_path: Optional[str] = None

class ThreatScore(BaseModel):
    pid: int
    score: float
    reasoning: str
    timestamp: float

# ===== NEW ENTERPRISE MODELS (ADD THESE) =====

class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    org_id: str
    password: Optional[str] = None
    token: Optional[str] = None

class Organization(BaseModel):
    org_id: str
    name: str
    created_at: int

class ResponseAction(str, Enum):
    QUARANTINE = "quarantine"
    BLOCK = "block"
    KILL_PROCESS = "kill_process"
    REVOKE_TOKEN = "revoke_token"
    ALERT = "alert"
    ISOLATE = "isolate"

class ResponsePlaybook(BaseModel):
    playbook_id: str
    org_id: str
    name: str
    trigger_severity: str  # "low", "medium", "high", "critical"
    actions: List[Dict]  # [{action: "quarantine", target: "agent"}, ...]
    enabled: bool

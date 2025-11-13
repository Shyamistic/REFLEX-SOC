from fastapi import APIRouter
from pydantic import BaseModel
import time
from typing import List, Dict
import requests

router = APIRouter(prefix="/response")

RESPONSE_LOGS = []
PLAYBOOKS = {}

class ResponsePlaybook(BaseModel):
    playbook_id: str
    org_id: str
    name: str
    trigger_severity: str
    actions: List[Dict]
    enabled: bool

class ExecutePlaybookRequest(BaseModel):
    playbook_id: str
    incident_id: int
    org_id: str

@router.post("/playbook/create")
def create_playbook(pb: ResponsePlaybook):
    PLAYBOOKS[pb.playbook_id] = pb.dict()
    return {"msg": "Playbook created", "playbook_id": pb.playbook_id}

@router.get("/playbooks")
def list_playbooks(org_id: str):
    return [pb for pb in PLAYBOOKS.values() if pb["org_id"] == org_id]

@router.post("/execute")
def execute_playbook(req: ExecutePlaybookRequest):
    if req.playbook_id not in PLAYBOOKS:
        return {"error": "Playbook not found"}
    
    pb = PLAYBOOKS[req.playbook_id]
    execution_log = {
        "execution_id": f"exec_{int(time.time())}",
        "playbook_id": req.playbook_id,
        "incident_id": req.incident_id,
        "org_id": req.org_id,
        "timestamp": int(time.time()),
        "actions_executed": []
    }
    
    for action in pb["actions"]:
        action_result = execute_action(action, req.incident_id)
        execution_log["actions_executed"].append(action_result)
    
    RESPONSE_LOGS.append(execution_log)
    return execution_log

def execute_action(action: Dict, incident_id: int) -> Dict:
    """Execute individual response action (NOW WITH REAL INTEGRATIONS)"""
    action_type = action.get("action")
    service = action.get("service", "internal")
    
    # Route to real integrations
    if service == "aws":
        return call_aws_integration(action, incident_id)
    elif service == "okta":
        return call_okta_integration(action, incident_id)
    elif service == "edr":
        return call_edr_integration(action, incident_id)
    else:
        # Fallback to internal action
        return internal_action(action_type, incident_id)

def call_aws_integration(action: Dict, incident_id: int) -> Dict:
    """Call AWS integration endpoint"""
    try:
        if action.get("action") == "isolate_sg":
            resp = requests.post("http://localhost:8899/integrations/aws/isolate", json={
                "action": "isolate_sg",
                "target": action.get("target", "sg-12345"),
                "description": f"Incident {incident_id}"
            })
        else:
            resp = requests.post("http://localhost:8899/integrations/aws/revoke_credentials", json={
                "action": "revoke_credentials",
                "target": action.get("target", "user-123"),
                "description": f"Incident {incident_id}"
            })
        return {"service": "aws", "status": "executed", "result": resp.json()}
    except Exception as e:
        return {"service": "aws", "status": "failed", "error": str(e)}

def call_okta_integration(action: Dict, incident_id: int) -> Dict:
    """Call Okta integration endpoint"""
    try:
        resp = requests.post(f"http://localhost:8899/integrations/okta/{action.get('action')}", json={
            "action": action.get("action"),
            "user_id": action.get("target", "user@company.com"),
            "reason": f"Incident {incident_id} - Auto-Response"
        })
        return {"service": "okta", "status": "executed", "result": resp.json()}
    except Exception as e:
        return {"service": "okta", "status": "failed", "error": str(e)}

def call_edr_integration(action: Dict, incident_id: int) -> Dict:
    """Call EDR integration endpoint"""
    try:
        resp = requests.post(f"http://localhost:8899/integrations/edr/{action.get('action')}", json={
            "action": action.get("action"),
            "endpoint_id": action.get("target", "endpoint-123"),
            "process_name": action.get("process"),
        })
        return {"service": "edr", "status": "executed", "result": resp.json()}
    except Exception as e:
        return {"service": "edr", "status": "failed", "error": str(e)}

def internal_action(action_type: str, incident_id: int) -> Dict:
    """Fallback internal action"""
    if action_type == "alert":
        return {"action": "alert", "status": "executed", "timestamp": int(time.time())}
    return {"action": action_type, "status": "unknown"}

@router.get("/logs")
def get_execution_logs(org_id: str):
    return [log for log in RESPONSE_LOGS if log["org_id"] == org_id]

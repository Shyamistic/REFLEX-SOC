from fastapi import APIRouter
from pydantic import BaseModel
import time
import json

router = APIRouter(prefix="/integrations")

# Simulated API credentials (use environment variables in production)
AWS_CONFIG = {"access_key": "demo_key", "secret": "demo_secret", "region": "us-east-1"}
OKTA_CONFIG = {"api_key": "demo_okta_key", "org_url": "https://demo.okta.com"}
EDR_CONFIG = {"api_key": "demo_edr_key", "endpoint": "https://demo-edr.api.com"}

INTEGRATION_LOGS = []

class AWSAction(BaseModel):
    action: str  # "isolate_sg", "revoke_credentials"
    target: str  # security group ID, user ID, etc.
    description: str

class OktaAction(BaseModel):
    action: str  # "revoke_token", "disable_user", "force_logout"
    user_id: str
    reason: str

class EDRAction(BaseModel):
    action: str  # "kill_process", "quarantine_endpoint", "isolate_host"
    endpoint_id: str
    process_name: str = None

# ===== AWS SECURITY GROUP ISOLATION =====

@router.post("/aws/isolate")
def aws_isolate_sg(action: AWSAction):
    """
    Isolate compromised instance by modifying security group
    Simulated: In production, call real boto3 with AWS credentials
    """
    log_entry = {
        "service": "AWS",
        "action": action.action,
        "target": action.target,
        "timestamp": int(time.time()),
        "status": "executed",
        "details": {
            "sg_id": action.target,
            "inbound_rules_removed": ["SSH", "RDP", "HTTP", "HTTPS"],
            "outbound_rules_removed": ["*"],
            "effect": "Instance isolated from network"
        }
    }
    INTEGRATION_LOGS.append(log_entry)
    print(f"🔒 AWS: Isolated security group {action.target}")
    return log_entry

@router.post("/aws/revoke_credentials")
def aws_revoke_creds(action: AWSAction):
    """Revoke compromised AWS IAM credentials"""
    log_entry = {
        "service": "AWS",
        "action": "revoke_credentials",
        "target": action.target,
        "timestamp": int(time.time()),
        "status": "executed",
        "details": {
            "access_keys_revoked": ["AKIA...xxxxx"],
            "effect": "Compromised credentials invalidated"
        }
    }
    INTEGRATION_LOGS.append(log_entry)
    print(f"🔐 AWS: Revoked credentials for {action.target}")
    return log_entry

# ===== OKTA TOKEN REVOCATION =====

@router.post("/okta/revoke_token")
def okta_revoke_token(action: OktaAction):
    """
    Revoke user sessions and tokens in Okta
    Effect: User is immediately logged out everywhere
    """
    log_entry = {
        "service": "Okta",
        "action": "revoke_token",
        "user_id": action.user_id,
        "timestamp": int(time.time()),
        "status": "executed",
        "details": {
            "sessions_revoked": 3,
            "tokens_revoked": ["token_xxx", "token_yyy"],
            "mfa_reset": True,
            "effect": "User immediately logged out from all sessions"
        }
    }
    INTEGRATION_LOGS.append(log_entry)
    print(f"🚫 Okta: Revoked all tokens for user {action.user_id}")
    return log_entry

@router.post("/okta/disable_user")
def okta_disable_user(action: OktaAction):
    """Disable Okta user account immediately"""
    log_entry = {
        "service": "Okta",
        "action": "disable_user",
        "user_id": action.user_id,
        "timestamp": int(time.time()),
        "status": "executed",
        "details": {
            "user_status": "disabled",
            "reason": action.reason,
            "access_removed": ["all_applications", "vpn", "network_access"],
            "effect": "User account fully disabled, cannot authenticate"
        }
    }
    INTEGRATION_LOGS.append(log_entry)
    print(f"🚷 Okta: Disabled user {action.user_id} - {action.reason}")
    return log_entry

@router.post("/okta/force_logout")
def okta_force_logout(action: OktaAction):
    """Force logout all user sessions in Okta"""
    log_entry = {
        "service": "Okta",
        "action": "force_logout",
        "user_id": action.user_id,
        "timestamp": int(time.time()),
        "status": "executed",
        "details": {
            "sessions_cleared": 5,
            "effect": "All user sessions terminated"
        }
    }
    INTEGRATION_LOGS.append(log_entry)
    print(f"🔌 Okta: Force logged out user {action.user_id}")
    return log_entry

# ===== EDR ENDPOINT RESPONSE =====

@router.post("/edr/kill_process")
def edr_kill_process(action: EDRAction):
    """Kill malicious process on endpoint via EDR agent"""
    log_entry = {
        "service": "EDR",
        "action": "kill_process",
        "endpoint_id": action.endpoint_id,
        "timestamp": int(time.time()),
        "status": "executed",
        "details": {
            "process_name": action.process_name,
            "pid": 1234,
            "killed": True,
            "effect": f"Process {action.process_name} terminated"
        }
    }
    INTEGRATION_LOGS.append(log_entry)
    print(f"💀 EDR: Killed process {action.process_name} on {action.endpoint_id}")
    return log_entry

@router.post("/edr/quarantine")
def edr_quarantine(action: EDRAction):
    """Quarantine endpoint (disable network, isolate from domain)"""
    log_entry = {
        "service": "EDR",
        "action": "quarantine_endpoint",
        "endpoint_id": action.endpoint_id,
        "timestamp": int(time.time()),
        "status": "executed",
        "details": {
            "network_isolation": True,
            "domain_removed": True,
            "file_system_protected": True,
            "effect": "Endpoint quarantined and isolated from network"
        }
    }
    INTEGRATION_LOGS.append(log_entry)
    print(f"⛔ EDR: Quarantined endpoint {action.endpoint_id}")
    return log_entry

@router.post("/edr/isolate_host")
def edr_isolate_host(action: EDRAction):
    """Completely isolate host from network"""
    log_entry = {
        "service": "EDR",
        "action": "isolate_host",
        "endpoint_id": action.endpoint_id,
        "timestamp": int(time.time()),
        "status": "executed",
        "details": {
            "network_disabled": True,
            "vpn_disconnected": True,
            "wifi_disabled": True,
            "effect": "Host fully isolated from all networks"
        }
    }
    INTEGRATION_LOGS.append(log_entry)
    print(f"🔒 EDR: Isolated host {action.endpoint_id} from all networks")
    return log_entry

# ===== INTEGRATION LOGS & HEALTH =====

@router.get("/logs")
def get_integration_logs(limit: int = 50):
    """Get history of all integration actions executed"""
    return list(INTEGRATION_LOGS)[-limit:]

@router.get("/health")
def check_integration_health():
    """Check health of all integrations"""
    return {
        "aws": {"status": "connected", "last_action": int(time.time())},
        "okta": {"status": "connected", "last_action": int(time.time())},
        "edr": {"status": "connected", "last_action": int(time.time())}
    }

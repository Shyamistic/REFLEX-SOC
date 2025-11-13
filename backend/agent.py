from fastapi import APIRouter
from pydantic import BaseModel
import time
from threat_engine import calculate_threat_score_with_ml, correlate_events, auto_respond, INCIDENTS, get_ml_stats

router = APIRouter(prefix="/agent")

# Org-isolated data stores
AGENTS_BY_ORG = {}
EVENTS_BY_ORG = {}

class Registration(BaseModel):
    agent_id: str
    hostname: str
    ip: str
    os: str
    version: str
    org_id: str

class Heartbeat(BaseModel):
    agent_id: str
    org_id: str

class Event(BaseModel):
    agent_id: str
    event_type: str
    timestamp: int
    details: dict
    org_id: str

@router.post("/register")
def register_agent(info: Registration):
    org_id = info.org_id
    if org_id not in AGENTS_BY_ORG:
        AGENTS_BY_ORG[org_id] = {}
    
    AGENTS_BY_ORG[org_id][info.agent_id] = {
        "hostname": info.hostname,
        "ip": info.ip,
        "os": info.os,
        "version": info.version,
        "last_seen": int(time.time()),
        "status": "online"
    }
    return {"msg": "Agent registered", "agent_id": info.agent_id, "org_id": org_id}

@router.post("/heartbeat")
def agent_heartbeat(hb: Heartbeat):
    org_id = hb.org_id
    if org_id in AGENTS_BY_ORG and hb.agent_id in AGENTS_BY_ORG[org_id]:
        AGENTS_BY_ORG[org_id][hb.agent_id]["last_seen"] = int(time.time())
        AGENTS_BY_ORG[org_id][hb.agent_id]["status"] = "online"
        return {"msg": "Heartbeat OK"}
    return {"error": "Unknown agent"}, 404

@router.post("/event")
def receive_event(event: Event):
    org_id = event.org_id
    if org_id not in EVENTS_BY_ORG:
        EVENTS_BY_ORG[org_id] = []
    
    evt_dict = event.dict()
    threat_score = calculate_threat_score_with_ml(evt_dict)  # CHANGED THIS LINE
    evt_dict["threat_score"] = threat_score
    
    EVENTS_BY_ORG[org_id].append(evt_dict)
    
    # Auto-trigger response if high severity
    if threat_score > 60:
        print(f"⚠️ HIGH THREAT for org {org_id}: Triggering auto-response")
        new_incidents = correlate_events(EVENTS_BY_ORG[org_id])
        for inc in new_incidents:
            print(f"🚨 AUTO-RESPONSE INITIATED: {inc}")
    
    if len(EVENTS_BY_ORG[org_id]) > 1000:
        EVENTS_BY_ORG[org_id].pop(0)
    
    return {"msg": "Event logged", "threat_score": threat_score, "org_id": org_id}

@router.get("/events")
def get_events(org_id: str, limit: int = 25):
    if org_id not in EVENTS_BY_ORG:
        return []
    return list(EVENTS_BY_ORG[org_id])[-limit:]

@router.get("/incidents")
def get_incidents():
    return INCIDENTS

@router.get("/online")
def online_agents(org_id: str):
    if org_id not in AGENTS_BY_ORG:
        return []
    cutoff = int(time.time()) - 120
    return [
        {"agent_id": a, **v}
        for a, v in AGENTS_BY_ORG[org_id].items()
        if v["last_seen"] >= cutoff
    ]

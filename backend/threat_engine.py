from ml_engine import detector
import time
from collections import defaultdict

INCIDENTS = []
INCIDENT_COUNTER = 0

def calculate_threat_score_with_ml(event):
    """Score using both rules and ML"""
    # Rule-based score
    THREAT_RULES = {
        "curl": 80,
        "bash": 50,
        "network_connection": 40,
        "file_write": 30,
    }
    
    score = 0
    process = event.get("details", {}).get("process", "")
    event_type = event.get("event_type", "")
    
    for keyword, weight in THREAT_RULES.items():
        if keyword in process or keyword in event_type:
            score += weight
    
    # ML anomaly boost
    ml_result = detector.detect_anomaly(event)
    if ml_result["is_anomaly"]:
        score += int(ml_result["anomaly_score"] * 30)
        event["ml_detected"] = True
        event["anomaly_score"] = ml_result["anomaly_score"]
    
    return min(score, 100)

def correlate_events(events):
    """Group related events into incidents"""
    global INCIDENT_COUNTER
    agent_events = defaultdict(list)
    
    for e in events[-50:]:
        agent_events[e["agent_id"]].append(e)
    
    new_incidents = []
    for agent_id, evt_list in agent_events.items():
        # Train ML on baseline first
        detector.learn_baseline(evt_list)
        
        high_score_events = [e for e in evt_list if calculate_threat_score_with_ml(e) > 60]
        if len(high_score_events) >= 2:
            INCIDENT_COUNTER += 1
            incident = {
                "incident_id": INCIDENT_COUNTER,
                "agent_id": agent_id,
                "severity": "high",
                "event_count": len(high_score_events),
                "timestamp": int(time.time()),
                "events": high_score_events,
                "status": "active",
                "ml_detected": sum(1 for e in high_score_events if e.get("ml_detected"))
            }
            new_incidents.append(incident)
    
    INCIDENTS.extend(new_incidents)
    if len(INCIDENTS) > 50:
        INCIDENTS[:] = INCIDENTS[-50:]
    
    return new_incidents

def auto_respond(incident):
    """Auto-execute response actions"""
    responses = []
    if incident["severity"] == "high":
        ml_count = incident.get("ml_detected", 0)
        if ml_count > 0:
            responses.append(f"🤖 ML ALERT: {ml_count} events flagged as anomalies")
        responses.append(f"ALERT: High-severity incident {incident['incident_id']}")
        responses.append(f"ACTION: Agent quarantine initiated")
    return responses

def get_ml_stats():
    """Get ML detection statistics"""
    return detector.get_detection_stats()

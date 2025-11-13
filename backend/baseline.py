from fastapi import APIRouter, HTTPException, Body
from models import Baseline, BaselineEntry, Policy

router = APIRouter(prefix="/baseline")

BASELINE = Baseline(entries=[])
POLICY = Policy(allow=["python", "flask"], block=["bash", "sleep", "socat"])

@router.get("/")
def get_baseline():
    return BASELINE

@router.post("/entry")
def add_entry(entry: BaselineEntry):
    BASELINE.entries.append(entry)
    return {"msg": "Entry added", "baseline_size": len(BASELINE.entries)}

@router.get("/policy")
def get_policy():
    return POLICY

@router.post("/policy", response_model=dict)
def set_policy(policy: Policy = Body(...)):
    global POLICY
    POLICY = policy
    return {"msg": "Policy updated"}

@router.get("/allowlist")
def get_allowlist():
    return {"allow": POLICY.allow}

@router.get("/blocklist")
def get_blocklist():
    return {"block": POLICY.block}

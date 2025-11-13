from fastapi import APIRouter
from models import ThreatScore
from pydantic import BaseModel
import random
import time

router = APIRouter(prefix="/ml")

class ProcessFeatures(BaseModel):
    pid: int
    parent_pid: int
    command_line: str
    ancestry: list[int] = []
    timestamp: float = None
    user: str = None
    env: dict = None

@router.post("/score", response_model=ThreatScore)
def score_process(features: ProcessFeatures):
    suspicious_keywords = ["sleep", "bash", "curl", "wget", "nc"]
    baseline_keywords = ["nginx", "gunicorn", "flask", "python", "node"]

    score = 0.1  # default benign
    reasoning = "Process appears benign"

    for kw in suspicious_keywords:
        if kw in features.command_line:
            score = random.uniform(0.7, 0.99)
            reasoning = f"Suspicious keyword found: {kw}"
            break
    else:
        for kw in baseline_keywords:
            if kw in features.command_line:
                score = 0.05
                reasoning = f"Baseline keyword found: {kw}"
                break

    return ThreatScore(
        pid=features.pid,
        score=score,
        reasoning=reasoning,
        timestamp=time.time()
    )

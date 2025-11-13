from fastapi import APIRouter, Response
from models import Evidence
import time
import csv
import io

router = APIRouter(prefix="/forensics")
EVIDENCES = []

@router.post("/")
def add_evidence(ev: Evidence):
    EVIDENCES.append(ev)
    return {"msg": "Evidence added", "count": len(EVIDENCES)}

@router.get("/")
def get_all_evidence():
    return EVIDENCES

@router.get("/export")
def export_evidence(format: str = "csv"):
    if format == "csv":
        output = io.StringIO()
        # If there is no evidence, just return the header for CSV
        if not EVIDENCES:
            # Use the Evidence model fields for the header
            # Update these if your Evidence model changes
            output.write("id,type,created,summary,file_path\n")
            return Response(content=output.getvalue(), media_type="text/csv")
        writer = csv.DictWriter(output, fieldnames=EVIDENCES[0].dict().keys())
        writer.writeheader()
        for ev in EVIDENCES:
            writer.writerow(ev.dict())
        return Response(content=output.getvalue(), media_type="text/csv")
    return EVIDENCES  # Default JSON
# Add this after EVIDENCES = []
EVIDENCES.append(Evidence(
    id="1",
    type="demo",
    created=int(time.time()),
    summary="This is a sample evidence entry.",
    file_path="/tmp/demo.txt"
))

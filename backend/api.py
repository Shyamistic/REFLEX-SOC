from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent import router as agent_router
from auth import router as auth_router
from response import router as response_router
from integrations import router as integrations_router
from baseline import router as baseline_router
from forensics import router as forensics_router
from saas import router as saas_router
from ml_engine import detector
import json

app = FastAPI(title="REFLEX - Autonomous SOC Platform v4.0 (ML + SaaS)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== INITIALIZE DEFAULT ORG ON STARTUP =====
@app.on_event("startup")
def startup_event():
    """Create default organization on startup"""
    from saas import ORGANIZATIONS, ORG_SUBSCRIPTIONS
    
    default_org = {
        "org_id": "default_org",
        "org_name": "Default Organization",
        "admin_email": "admin@reflex.local",
        "subscription_tier": "pro",
        "created_at": 1699849200,
        "agents_limit": 50,
        "users_limit": 20,
        "agents_used": 1,
        "users_used": 1,
        "status": "active"
    }
    
    ORGANIZATIONS["default_org"] = default_org
    ORG_SUBSCRIPTIONS["default_org"] = {
        "tier": "pro",
        "monthly_price": 499,
        "renewal_date": 1704033200
    }
    print("✅ Default organization initialized")

# Include all routers
app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(response_router)
app.include_router(integrations_router)
app.include_router(baseline_router)
app.include_router(forensics_router)
app.include_router(saas_router)

@app.get("/")
def root():
    return {
        "name": "REFLEX SOC v4.0",
        "version": "4.0",
        "status": "autonomous",
        "features": [
            "multi_tenant",
            "real_api_integrations",
            "ml_detection",
            "saas_billing"
        ],
        "ml_status": detector.get_detection_stats()
    }

@app.get("/ml/stats")
def get_ml_stats():
    """Get ML detection statistics"""
    return detector.get_detection_stats()

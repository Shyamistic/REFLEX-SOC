from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import time
import uuid

router = APIRouter(prefix="/saas")

# Multi-org data store
ORGANIZATIONS = {}
ORG_USERS = {}  # org_id -> [users]
ORG_SUBSCRIPTIONS = {}  # org_id -> subscription tier
BILLING_RECORDS = {}  # org_id -> [billing entries]

class OrgCreateRequest(BaseModel):
    org_name: str
    admin_email: str
    subscription_tier: str  # "starter", "pro", "enterprise"

class OrgResponse(BaseModel):
    org_id: str
    org_name: str
    admin_email: str
    subscription_tier: str
    created_at: int
    agents_limit: int
    users_limit: int

class UserCreateRequest(BaseModel):
    org_id: str
    username: str
    email: str
    role: str  # "admin", "analyst", "viewer"

@router.post("/org/create")
def create_organization(req: OrgCreateRequest):
    """Create new customer organization"""
    org_id = str(uuid.uuid4())[:8]
    
    # Tier-based limits
    tier_limits = {
        "starter": {"agents": 5, "users": 3, "price": 99},
        "pro": {"agents": 50, "users": 20, "price": 499},
        "enterprise": {"agents": 500, "users": 100, "price": 2999}
    }
    limits = tier_limits.get(req.subscription_tier, tier_limits["starter"])
    
    org_data = {
        "org_id": org_id,
        "org_name": req.org_name,
        "admin_email": req.admin_email,
        "subscription_tier": req.subscription_tier,
        "created_at": int(time.time()),
        "agents_limit": limits["agents"],
        "users_limit": limits["users"],
        "agents_used": 0,
        "users_used": 1,
        "status": "active"
    }
    
    ORGANIZATIONS[org_id] = org_data
    OrgCreateRequest[org_id] = []
    ORG_SUBSCRIPTIONS[org_id] = {
        "tier": req.subscription_tier,
        "monthly_price": limits["price"],
        "renewal_date": int(time.time()) + 30*24*3600
    }
    
    return OrgResponse(**org_data)

@router.get("/org/list")
def list_organizations():
    """List all organizations (admin only in production)"""
    return list(ORGANIZATIONS.values())

@router.get("/org/{org_id}")
def get_organization(org_id: str):
    """Get org details"""
    if org_id not in ORGANIZATIONS:
        raise HTTPException(status_code=404, detail="Organization not found")
    return ORGANIZATIONS[org_id]

@router.post("/org/{org_id}/user/add")
def add_user_to_org(org_id: str, req: UserCreateRequest):
    """Add user to organization"""
    if org_id not in ORGANIZATIONS:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    org = ORGANIZATIONS[org_id]
    if org["users_used"] >= org["users_limit"]:
        raise HTTPException(status_code=400, detail="User limit reached")
    
    if org_id not in ORG_USERS:
        ORG_USERS[org_id] = []
    
    user = {
        "username": req.username,
        "email": req.email,
        "role": req.role,
        "created_at": int(time.time())
    }
    
    ORG_USERS[org_id].append(user)
    org["users_used"] += 1
    
    return {"msg": "User added", "user": user}

@router.get("/org/{org_id}/users")
def get_org_users(org_id: str):
    """Get all users in organization"""
    if org_id not in ORGANIZATIONS:
        raise HTTPException(status_code=404, detail="Organization not found")
    return ORG_USERS.get(org_id, [])

@router.get("/billing/{org_id}")
def get_billing_info(org_id: str):
    """Get billing and subscription info"""
    if org_id not in ORGANIZATIONS:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    org = ORGANIZATIONS[org_id]
    subscription = ORG_SUBSCRIPTIONS.get(org_id, {})
    
    return {
        "org_id": org_id,
        "org_name": org["org_name"],
        "subscription_tier": org["subscription_tier"],
        "monthly_price": subscription.get("monthly_price", 0),
        "renewal_date": subscription.get("renewal_date"),
        "agents_used": org["agents_used"],
        "agents_limit": org["agents_limit"],
        "users_used": org["users_used"],
        "users_limit": org["users_limit"],
        "status": org["status"]
    }

@router.post("/org/{org_id}/upgrade")
def upgrade_subscription(org_id: str, new_tier: str):
    """Upgrade organization subscription"""
    if org_id not in ORGANIZATIONS:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    tier_limits = {
        "starter": {"agents": 5, "users": 3, "price": 99},
        "pro": {"agents": 50, "users": 20, "price": 499},
        "enterprise": {"agents": 500, "users": 100, "price": 2999}
    }
    
    if new_tier not in tier_limits:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    org = ORGANIZATIONS[org_id]
    limits = tier_limits[new_tier]
    
    org["subscription_tier"] = new_tier
    org["agents_limit"] = limits["agents"]
    org["users_limit"] = limits["users"]
    
    ORG_SUBSCRIPTIONS[org_id] = {
        "tier": new_tier,
        "monthly_price": limits["price"],
        "renewal_date": int(time.time()) + 30*24*3600
    }
    
    return {"msg": f"Upgraded to {new_tier}", "org": org}

@router.get("/analytics/platform")
def get_platform_analytics():
    """Get platform-wide analytics (dashboard for SaaS admin)"""
    total_orgs = len(ORGANIZATIONS)
    total_users = sum(len(users) for users in ORG_USERS.values())
    total_revenue = sum(
        ORG_SUBSCRIPTIONS.get(org_id, {}).get("monthly_price", 0) 
        for org_id in ORGANIZATIONS.keys()
    )
    
    tier_breakdown = {}
    for org in ORGANIZATIONS.values():
        tier = org["subscription_tier"]
        tier_breakdown[tier] = tier_breakdown.get(tier, 0) + 1
    
    return {
        "total_organizations": total_orgs,
        "total_users": total_users,
        "monthly_recurring_revenue": total_revenue,
        "tier_breakdown": tier_breakdown,
        "timestamp": int(time.time())
    }

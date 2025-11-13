from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import time

router = APIRouter(prefix="/auth")

# Pre-populated users database
USERS = {
    "analyst": {"password": "analyst123", "role": "analyst", "org_id": "default_org", "token": None},
    "admin": {"password": "admin123", "role": "admin", "org_id": "default_org", "token": None}
}

class LoginRequest(BaseModel):
    username: str
    password: str
    org_id: str

class AuthResponse(BaseModel):
    user_id: str
    username: str
    role: str
    org_id: str
    token: str

@router.post("/login")
def login(req: LoginRequest):
    """Simple multi-tenant login"""
    if req.username not in USERS:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = USERS[req.username]
    if user["password"] != req.password or user["org_id"] != req.org_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = f"token_{req.username}_{int(time.time())}"
    user["token"] = token
    
    return AuthResponse(
        user_id=req.username,
        username=req.username,
        role=user["role"],
        org_id=req.org_id,
        token=token
    )

@router.get("/me")
def get_me(token: str = Header(...)):
    """Get current user"""
    for username, data in USERS.items():
        if data.get("token") == token:
            return {"username": username, "role": data["role"], "org_id": data["org_id"]}
    raise HTTPException(status_code=401, detail="Invalid token")

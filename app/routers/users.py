from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.dependencies.db import get_db
import hashlib
import os


router = APIRouter()


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: str
    username: str
    createdAt: str


@router.post("/users", response_model=UserOut)
async def create_user(payload: UserCreate):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    # generate salt per user
    salt = os.urandom(16).hex()
    pwd_hash = hash_password(payload.password, salt)
    doc = {
        "_id": f"user_{payload.username}",
        "username": payload.username,
        "passwordHash": pwd_hash,
        "passwordSalt": salt,
        "createdAt": now,
        "updatedAt": now,
    }
    try:
        await db.users.insert_one(doc)
    except Exception as e:
        # likely duplicate username
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"id": doc["_id"], "username": payload.username, "createdAt": now}


@router.get("/users", response_model=List[UserOut])
async def list_users(limit: int = 100):
    db = get_db()
    cur = db.users.find({}, {"passwordHash": 0, "passwordSalt": 0}).limit(min(limit, 200))
    return [UserOut(id=d["_id"], username=d.get("username"), createdAt=d.get("createdAt")) async for d in cur]


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    db = get_db()
    u = await db.users.find_one({"_id": user_id}, {"passwordHash": 0, "passwordSalt": 0})
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    u["id"] = u.pop("_id")
    return u


class UserUpdate(BaseModel):
    password: str | None = None


@router.patch("/users/{user_id}")
async def update_user(user_id: str, payload: UserUpdate):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    update = {"updatedAt": now}
    if payload.password:
        salt = os.urandom(16).hex()
        update["passwordSalt"] = salt
        update["passwordHash"] = hash_password(payload.password, salt)
    res = await db.users.update_one({"_id": user_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    db = get_db()
    res = await db.users.delete_one({"_id": user_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


class LoginIn(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
async def login(payload: LoginIn):
    db = get_db()
    user = await db.users.find_one({"username": payload.username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    salt = user.get("passwordSalt")
    if not salt:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if hash_password(payload.password, salt) != user.get("passwordHash"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # For now, return a simple session object; future: JWT or API key issuance
    return {"ok": True, "userId": user["_id"], "username": user.get("username")}



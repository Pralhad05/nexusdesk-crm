from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token
from app.auth import get_password_hash, verify_password, create_access_token
from sqlalchemy import select

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Return token
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_id": new_user.id, "purpose": new_user.purpose}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "purpose": user.purpose}

@router.post("/setup-purpose")
async def setup_purpose(data: dict, db: AsyncSession = Depends(get_db)):
    # Simplified for frontend - expects user_id and purpose in data
    from app.auth import create_access_token
    from jose import jwt, JWTError
    import os
    
    token = data.get("token")
    purpose = data.get("purpose")
    
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY", "super-secret-change-in-production"), algorithms=["HS256"])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.purpose = purpose
    await db.commit()
    
    new_token = create_access_token(data={"sub": user.email})
    return {"access_token": new_token, "token_type": "bearer", "user_id": user.id, "purpose": purpose}
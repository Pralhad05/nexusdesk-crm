from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional
from jose import jwt, JWTError
import os
from app.database import get_db
from app.models import Ticket, User
from app.schemas import TicketCreate, TicketCreateResponse, TicketDetail, TicketUpdate
from app import crud

router = APIRouter(prefix="/api/tickets", tags=["tickets"])
security = HTTPBearer()

# Helper to get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, os.getenv("SECRET_KEY", "super-secret-change-in-production"), algorithms=["HS256"])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user: 
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("", response_model=TicketCreateResponse, status_code=201)
async def create_ticket(ticket_data: TicketCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        # FIXED: Passing owner_id here
        ticket = await crud.create_ticket(db, ticket_data, owner_id=user.id)
        return TicketCreateResponse(ticket_id=ticket.ticket_id, created_at=ticket.created_at)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("")
async def list_tickets(status: Optional[str] = Query(None), search: Optional[str] = Query(None), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # FIXED: Passing owner_id here
    return await crud.get_tickets(db, owner_id=user.id, status=status, search=search)

@router.get("/stats")
async def get_stats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # FIXED: Passing owner_id here
    return await crud.get_ticket_stats(db, owner_id=user.id)

@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket(ticket_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # FIXED: Passing owner_id here
    ticket = await crud.get_ticket_by_id(db, ticket_id, owner_id=user.id)
    if not ticket: 
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.put("/{ticket_id}")
async def update_ticket(ticket_id: str, update_data: TicketUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not update_data.status and not update_data.notes: 
        raise HTTPException(status_code=400, detail="Must provide status or notes")
    # FIXED: Passing owner_id here
    ticket = await crud.update_ticket(db, ticket_id, owner_id=user.id, update_data=update_data)
    if not ticket: 
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"success": True, "updated_at": ticket.updated_at}
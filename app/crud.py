from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime, timezone
from app.models import Ticket, Note
from app.schemas import TicketCreate, TicketUpdate

async def generate_ticket_id(db: AsyncSession) -> str:
    """Generate a globally unique ticket ID across ALL users"""
    result = await db.execute(select(func.count()).select_from(Ticket))
    count = result.scalar() or 0
    return f"TKT-{count + 1:03d}"

async def create_ticket(db: AsyncSession, ticket_data: TicketCreate, owner_id: int) -> Ticket:
    ticket_id = await generate_ticket_id(db)
    ticket = Ticket(
        ticket_id=ticket_id,
        customer_name=ticket_data.customer_name,
        customer_email=ticket_data.customer_email,
        subject=ticket_data.subject,
        description=ticket_data.description,
        status="Open",
        owner_id=owner_id
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket

async def get_tickets(db: AsyncSession, owner_id: int, status: Optional[str] = None, search: Optional[str] = None):
    query = select(Ticket).where(Ticket.owner_id == owner_id).order_by(Ticket.created_at.desc())
    if status:
        query = query.where(Ticket.status == status)
    if search:
        search_term = f"%{search}%"
        query = query.where(or_(
            Ticket.ticket_id.ilike(search_term), Ticket.customer_name.ilike(search_term),
            Ticket.customer_email.ilike(search_term), Ticket.subject.ilike(search_term),
            Ticket.description.ilike(search_term)
        ))
    result = await db.execute(query)
    return result.scalars().all()

async def get_ticket_stats(db: AsyncSession, owner_id: int):
    total = await db.execute(select(func.count()).select_from(Ticket).where(Ticket.owner_id == owner_id))
    open_count = await db.execute(select(func.count()).select_from(Ticket).where(Ticket.owner_id == owner_id, Ticket.status == "Open"))
    progress_count = await db.execute(select(func.count()).select_from(Ticket).where(Ticket.owner_id == owner_id, Ticket.status == "In Progress"))
    closed_count = await db.execute(select(func.count()).select_from(Ticket).where(Ticket.owner_id == owner_id, Ticket.status == "Closed"))
    return {"total": total.scalar() or 0, "open": open_count.scalar() or 0, "in_progress": progress_count.scalar() or 0, "closed": closed_count.scalar() or 0}

async def get_ticket_by_id(db: AsyncSession, ticket_id: str, owner_id: int) -> Optional[Ticket]:
    query = select(Ticket).options(selectinload(Ticket.notes)).where(Ticket.ticket_id == ticket_id, Ticket.owner_id == owner_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_ticket(db: AsyncSession, ticket_id: str, owner_id: int, update_data: TicketUpdate) -> Optional[Ticket]:
    ticket = await get_ticket_by_id(db, ticket_id, owner_id)
    if not ticket: return None
    
    if update_data.status:
        ticket.status = update_data.status
        ticket.updated_at = datetime.now(timezone.utc)
    if update_data.notes:
        note = Note(ticket_id=ticket_id, note_text=update_data.notes)
        db.add(note)
        ticket.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(ticket)
    return ticket
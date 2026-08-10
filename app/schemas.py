from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# --- Ticket Schemas ---
class TicketCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_email: EmailStr
    subject: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)

class TicketCreateResponse(BaseModel):
    ticket_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class NoteResponse(BaseModel):
    id: int
    note_text: str
    created_at: datetime
    class Config:
        from_attributes = True

class TicketDetail(BaseModel):
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    notes: List[NoteResponse] = []
    class Config:
        from_attributes = True

class TicketUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(Open|In Progress|Closed)$")
    notes: Optional[str] = None

# --- Auth Schemas (ADD THESE) ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    purpose: Optional[str] = None
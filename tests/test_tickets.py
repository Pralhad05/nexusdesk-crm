import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db, async_session, engine, Base
from app.models import Ticket, Note
import asyncio


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_ticket():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/tickets", json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "subject": "Test Issue",
            "description": "This is a test description"
        })
    
    assert response.status_code == 201
    data = response.json()
    assert data["ticket_id"] == "TKT-001"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_tickets():
    # Create a ticket first
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/tickets", json={
            "customer_name": "Jane Doe",
            "customer_email": "jane@example.com",
            "subject": "Another Issue",
            "description": "Another description"
        })
        
        response = await client.get("/api/tickets")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["ticket_id"] is not None


@pytest.mark.asyncio
async def test_search_tickets():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create ticket
        await client.post("/api/tickets", json={
            "customer_name": "Search Test User",
            "customer_email": "search@test.com",
            "subject": "Searchable Subject",
            "description": "Searchable description"
        })
        
        # Search
        response = await client.get("/api/tickets?search=Search Test User")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_filter_by_status():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/tickets?status=Open")
    
    assert response.status_code == 200
    data = response.json()
    for ticket in data:
        assert ticket["status"] == "Open"


@pytest.mark.asyncio
async def test_get_ticket_detail():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create ticket
        create_response = await client.post("/api/tickets", json={
            "customer_name": "Detail Test",
            "customer_email": "detail@test.com",
            "subject": "Detail Subject",
            "description": "Detail description"
        })
        ticket_id = create_response.json()["ticket_id"]
        
        # Get detail
        response = await client.get(f"/api/tickets/{ticket_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == ticket_id
    assert data["customer_name"] == "Detail Test"
    assert "notes" in data


@pytest.mark.asyncio
async def test_update_ticket():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create ticket
        create_response = await client.post("/api/tickets", json={
            "customer_name": "Update Test",
            "customer_email": "update@test.com",
            "subject": "Update Subject",
            "description": "Update description"
        })
        ticket_id = create_response.json()["ticket_id"]
        
        # Update ticket
        response = await client.put(f"/api/tickets/{ticket_id}", json={
            "status": "In Progress",
            "notes": "Working on this issue"
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_nonexistent_ticket():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/tickets/TKT-99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_stats():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/tickets/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "open" in data
    assert "in_progress" in data
    assert "closed" in data
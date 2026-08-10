from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from contextlib import asynccontextmanager
from app.database import init_db
from app.routers import tickets, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Environment(loader=FileSystemLoader("templates"))

def render(template_name: str, context: dict) -> HTMLResponse:
    template = templates.get_template(template_name)
    return HTMLResponse(template.render(**context))

app.include_router(tickets.router)
app.include_router(auth.router)

# --- PAGE ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return render("landing.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return render("auth.html", {"request": request})

@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    return render("setup.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return render("index.html", {"request": request})

@app.get("/create", response_class=HTMLResponse)
async def create_page(request: Request):
    return render("create.html", {"request": request})

@app.get("/tickets/{ticket_id}", response_class=HTMLResponse)
async def ticket_detail_page(request: Request, ticket_id: str):
    return render("detail.html", {"request": request, "ticket_id": ticket_id})
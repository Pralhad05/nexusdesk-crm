NexusDesk: Multi-Tenant Support CRM
A production-grade, multi-tenant customer support ticketing system built with modern async Python. Designed to handle hundreds of support agents working concurrently, with complete data isolation and a premium UI.

🚀 Live Demo
URL: https://nexusdeskcrmpg.onrender.com/

📸 Demo Video
Video Link: https://drive.google.com/file/d/1WAjyoZs2KfREAPuCdWV4Ky__g8quNmv3/view?usp=sharing

🏗️ Technical Approach & Architecture
I chose Python + FastAPI for the backend to leverage its native async capabilities, paired with SQLite for zero-configuration persistence and Tailwind CSS for a modern, responsive frontend without the overhead of a heavy JS framework.

The "Stand Out" Feature: Multi-Tenant Data Isolation
While the core spec asked for a simple ticketing system, a real support team cannot operate on a single shared dashboard where everyone sees everyone else's tickets.

Instead of taking the easy route and skipping authentication (as suggested in the rubric), I implemented stateless JWT authentication with row-level security.

Every ticket is tied to an owner_id.
When agents query the database, the backend automatically injects a WHERE owner_id = ? clause.
The result: 100 agents can use the system simultaneously, completely isolated from one another, using a single lightweight SQLite file.
Database Design (Keep it simple, but smart)
Instead of creating a new .db file for every user (which breaks deployment and scalability), I used a single support_crm.db file with two tables:

tickets: Contains owner_id (Foreign Key to users) to achieve logical separation.
notes: Linked to tickets via ticket_id for activity tracking.
Concurrency Handling (WAL Mode)
Because SQLite traditionally locks the entire database during writes, I enabled WAL (Write-Ahead Logging) mode via SQLAlchemy events. This allows multiple agents to read ticket dashboards simultaneously while one agent is writing (creating/updating) a ticket, preventing database is locked errors at scale.

💻 Tech Stack
Backend: Python 3.11, FastAPI, Uvicorn
Database: SQLite (Async via aiosqlite, WAL mode enabled)
ORM: SQLAlchemy 2.0 (Async)
Auth: JWT (python-jose), Bcrypt (Direct implementation to bypass passlib version conflicts)
Frontend: Vanilla JavaScript (Fetch API), Tailwind CSS, Jinja2 Templates

✨ Key Features
Core Requirements Met
Create Tickets: Auto-generates unique IDs (e.g., TKT-001), captures customer info.
List All Tickets: Clean, animated list view with color-coded priority borders.
Search Functionality: Debounced real-time search across names, emails, IDs, and descriptions.
Filter by Status: Instantly filter by Open, In Progress, or Closed.
View & Update: Detailed view with timeline, internal activity notes, and status updates.
Standout Features Added
Premium Landing Page: Marketing page with dynamic floating elements and glassmorphism.
Secure Auth Flow: Register -> Alert Popup -> Login -> Dashboard.
Responsive Design: Fully mobile-optimized with custom hamburger menus.
Live Dashboard Stats: Real-time stat cards updating based on the logged-in user's data.

🛠️ Local Setup Instructions
Prerequisites
Python 3.11 or higher (3.14 is not recommended due to dependency compilation issues).
Git
Step-by-Step Execution
# 1. Clone the repositorygit clone https://github.com/Pralhad05/nexusdesk-crm.gitcd nexusdesk-crm
# 2. Create and activate virtual environmentpython -m venv venv
# On Windows:.\venv\Scripts\activate
# On Mac/Linux:source venv/bin/activate
# 3. Install dependenciespip install -r requirements.txt
# 4. Setup environment variablescp .env.example .env
# (The default .env is configured for local SQLite)
# 5. Run the applicationpython run.py
The application will automatically create the support_crm.db file and the required tables on startup.
Open http://localhost:8000 to view the landing page.

📡 API Endpoints (Simple REST)
All /api/tickets endpoints require an Authorization: Bearer <token> header.

Method
Endpoint
Description
POST	/api/auth/register	Register a new user
POST	/api/auth/login	Login and receive JWT token
POST	/api/tickets	Create a new ticket
GET	/api/tickets	List tickets (?status=Open&search=john)
GET	/api/tickets/stats	Get user's ticket statistics
GET	/api/tickets/{ticket_id}	Get detailed ticket + notes
PUT	/api/tickets/{ticket_id}	Update status and add notes

⚠️ Challenges Faced & Solutions
The passlib / bcrypt Version Conflict:
Challenge: The latest version of bcrypt (4.1+) removed __about__, causing passlib to crash with a ValueError during password hashing.
Solution: Bypassed passlib entirely and implemented password hashing and verification directly using the bcrypt library. It resulted in cleaner, more secure code.
SQLAlchemy Async "MissingGreenlet" Error:
Challenge: When fetching a ticket to view its notes, SQLAlchemy threw a MissingGreenlet error because related objects (notes) weren't being loaded in the async context.
Solution: Implemented selectinload(Ticket.notes) in the SQLAlchemy select statement to eagerly fetch relationships in a single async query.
Global vs. Local Ticket IDs:
Challenge: Initially, the ID generator counted tickets per user. This caused a UNIQUE constraint failed error when User A created TKT-001 and User B tried to create their first ticket.
Solution: Modified the generator to count all tickets globally to ensure absolute uniqueness across the multi-tenant platform.
Jinja2 Caching Bug:
Challenge: A recent update to Starlette/Jinja2 caused TypeError: cannot use 'tuple' as a dict key on template rendering.
Solution: Bypassed Starlette's Jinja2Templates and initialized standard jinja2.Environment directly in main.py to avoid the broken middleware.

🔮 Future Improvements
If I had another 2-3 days, I would implement:

WebSockets: Push real-time notifications to the dashboard when another agent updates a ticket.
Role-Based Access Control (RBAC): An "Admin" role to view all agents' tickets and run analytics.
PostgreSQL Migration: Swap SQLite for PostgreSQL to allow horizontal scaling across multiple Railway dynos if the user base grows past 10,000.

📧 Submission Details
Technical Approach: End-to-end async architecture focusing on multi-tenancy and concurrency.
Proud of: The seamless JWT integration that turns a simple script into a deployable SaaS platform.
Tradeoff made: Adding authentication increased the codebase complexity by ~30%, but it was a necessary tradeoff to demonstrate how a real CRM handles data privacy.
Built by Pralhad Gaikwad for Datastraw Technologies.

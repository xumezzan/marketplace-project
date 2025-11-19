# Services Marketplace MVP

A marketplace platform for connecting clients with service providers (like TaskRabbit/Profi.ru for local market).

## Tech Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL
- **Frontend**: Server-rendered HTML templates (responsive, mobile-friendly)
- **Containerization**: Docker & Docker Compose

## Project Structure

```
services-marketplace/
├── backend/              # Main Django project
│   ├── config/           # Project settings (Django config)
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── accounts/         # User model and authentication
│   ├── marketplace/      # Main marketplace app (tasks, offers, deals, reviews)
│   ├── templates/        # HTML templates
│   ├── static/           # Static files (CSS, JS, images)
│   ├── manage.py
│   └── requirements.txt
├── requirements.txt      # Root requirements (for deployment)
├── Procfile             # For Render.com deployment
├── render.yaml          # Render.com configuration
├── Dockerfile
└── docker-compose.yml
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL (or use Docker)
- Docker & Docker Compose (optional, for containerized setup)

### Option 1: Local Development (without Docker)

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Copy `.env.example` to `.env` and update values:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your settings. See `.env.example` for all available options.
   
   **Required variables:**
   - `DJANGO_SECRET_KEY` - Secret key for Django (generate a secure one for production)
   - `DJANGO_DEBUG=True` - Set to `False` in production
   - `DJANGO_ALLOWED_HOSTS` - Comma-separated list of allowed hosts
   
   **Optional variables:**
   - `DATABASE_URL` - PostgreSQL connection string (leave empty for SQLite)
   - `GEMINI_API_KEY` - For AI task analysis feature
   - `EMAIL_*` - For email notifications
   - `CACHE_URL` - For Redis/Memcached caching

4. **Create PostgreSQL database:**
   ```bash
   createdb marketplace_db
   ```

5. **Run migrations:**
   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   cd backend
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
   cd backend
   python manage.py runserver
   ```

8. **Access the application:**
   - Web app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

### Option 2: Docker Development

1. **Create `.env` file** (same as above)

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Create superuser (in another terminal):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the application:**
   - Web app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Database Models

### Core Entities

1. **User** - Custom user model with roles (client/specialist)
2. **Category** - Service categories (Repair, Tutor, Fitness, Beauty, etc.)
3. **SpecialistProfile** - Specialist-specific information
4. **Task** - Client service requests
5. **Offer** - Specialist responses to tasks
6. **Deal** - Completed agreements (optional for MVP)

## Next Steps

After setting up the project:

1. Create initial categories via admin panel
2. Implement user registration and login views
3. Create task creation forms
4. Build task browsing and filtering
5. Implement offer submission
6. Add offer acceptance flow
7. Create responsive frontend templates

## Development Commands

```bash
# Navigate to backend directory
cd backend

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests
python manage.py test

# Collect static files (for production)
python manage.py collectstatic --noinput
```

## Notes

- The project uses a custom User model (`accounts.User`)
- All models are registered in Django admin for easy management
- REST API endpoints are available at `/api/`
- Frontend templates use Bootstrap 5 for responsive design
- The project defaults to SQLite for local development
- PostgreSQL is used automatically on Render.com via `DATABASE_URL` environment variable


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
├── marketplace/          # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                # User model and authentication
├── categories/           # Service categories
├── tasks/                # Client task requests
├── offers/               # Specialist offers
├── specialists/          # Specialist profiles
├── deals/                # Completed deals/bookings
├── manage.py
├── requirements.txt
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
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=marketplace_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Create PostgreSQL database:**
   ```bash
   createdb marketplace_db
   ```

5. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**
   ```bash
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
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests (when implemented)
python manage.py test

# Collect static files
python manage.py collectstatic
```

## Notes

- The project uses a custom User model (`users.User`)
- All models are registered in Django admin for easy management
- REST API endpoints will be added in the next phase
- Frontend templates will use Bootstrap or Tailwind CSS for responsive design


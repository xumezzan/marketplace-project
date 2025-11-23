# Services Marketplace

A full-featured marketplace platform for connecting clients with service providers, similar to TaskRabbit or Profi.ru, tailored for the Uzbekistan market.

## Features

- **User Management**: Dual-role system (Clients & Specialists) with profiles
- **Task Management**: AI-powered task creation, browsing, and filtering
- **Real-time Chat**: WebSocket-based messaging with video call integration (Jitsi Meet)
- **Payments & Escrow**: Payme integration with 10% platform commission
- **Admin Panel**: Content moderation and dispute resolution
- **Analytics**: Specialist performance dashboards
- **API Documentation**: Interactive Swagger/ReDoc interface

## Tech Stack

- **Backend**: Django 4.2 (LTS) + Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Real-time**: Django Channels + Redis
- **Payments**: Payme (Uzbekistan)
- **AI**: Google Gemini API
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx + Gunicorn (production)

## Quick Start

### Option 1: Docker (Recommended for Production)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd services-marketplace
   ```

2. **Create environment file:**
   ```bash
   cp backend/.env.prod backend/.env.prod.local
   # Edit .env.prod.local with your production values
   ```

3. **Build and run:**
   ```bash
   cd backend
   docker-compose -f docker-compose.prod.yml up --build
   ```

4. **Create superuser:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

5. **Access the application:**
   - Web app: http://localhost
   - Admin panel: http://localhost/admin
   - API Docs: http://localhost/api/schema/swagger-ui/

### Option 2: Local Development

1. **Prerequisites:**
   - Python 3.9+
   - Redis (for Channels)
   - PostgreSQL (optional, defaults to SQLite)

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   cd backend
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Web app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - API Docs: http://localhost:8000/api/schema/swagger-ui/

## Environment Variables

### Required (Production)
- `DJANGO_SECRET_KEY` - Django secret key (generate securely)
- `DJANGO_ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_HOST` - Redis host (default: localhost)
- `REDIS_PORT` - Redis port (default: 6379)

### Optional
- `GEMINI_API_KEY` - Google Gemini API key for AI features
- `PAYME_KEY` - Payme merchant key for payment processing
- `EMAIL_HOST` - SMTP server for email notifications
- `EMAIL_HOST_USER` - SMTP username
- `EMAIL_HOST_PASSWORD` - SMTP password

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## Project Structure

```
services-marketplace/
├── backend/
│   ├── config/              # Django settings
│   │   ├── settings/        # Split settings (base, dev, prod)
│   │   ├── urls.py
│   │   ├── asgi.py          # ASGI config (Channels)
│   │   └── wsgi.py
│   ├── accounts/            # User authentication
│   ├── marketplace/         # Core marketplace logic
│   ├── payments/            # Payment & wallet system
│   ├── chat/                # Real-time chat & video
│   ├── notifications/       # Notification system
│   ├── static/              # Static files
│   ├── templates/           # HTML templates
│   ├── Dockerfile
│   ├── docker-compose.prod.yml
│   └── requirements.txt
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI
└── README.md
```

## Development

### Running Tests
```bash
cd backend
python manage.py test
```

### Linting
```bash
flake8 .
```

### Collecting Static Files
```bash
python manage.py collectstatic --noinput
```

## Deployment

The project is production-ready with:
- Docker containerization
- Nginx reverse proxy
- Gunicorn WSGI server
- WhiteNoise for static files
- PostgreSQL database
- Redis for Channels

See `backend/docker-compose.prod.yml` for the full production stack.

## License

MIT License

#!/usr/bin/env bash
# exit on error
set -o errexit

# Navigate to service_market_uz directory
cd service_market_uz

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create admin user if it doesn't exist
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('Creating admin user...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print('Admin user created successfully!')
else:
    print('Admin user already exists.')
END

echo "Build completed successfully!"

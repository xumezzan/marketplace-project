import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()
email = 'admin@example.com'
password = 'admin'

if not User.objects.filter(email=email).exists():
    print(f"Creating superuser {email}")
    User.objects.create_superuser(email=email, password=password, role='ADMIN', phone='+998901234567')
else:
    print("Superuser already exists")

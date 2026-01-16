from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='testuser').exists():
    u = User.objects.create_user('testuser', 'test@example.com', 'testpass')
    u.is_client = True
    u.is_specialist = True
    u.save()
    print("Test user created")
else:
    print("Test user already exists")

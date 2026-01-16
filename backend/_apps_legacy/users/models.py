from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, phone, password, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, phone, password, **extra_fields)

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self._create_user(email, phone, password, **extra_fields)

class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'CLIENT', _('Client')
        SPECIALIST = 'SPECIALIST', _('Specialist')
        ADMIN = 'ADMIN', _('Admin')
        MODERATOR = 'MODERATOR', _('Moderator')

    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone number'), max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    def __str__(self):
        return self.email

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    
    def __str__(self):
        return f"Client {self.user.email}"

class SpecialistProfile(models.Model):
    class Level(models.TextChoices):
        NEW = 'NEW', _('New')
        VERIFIED = 'VERIFIED', _('Verified')
        PRO = 'PRO', _('Pro')
        TOP = 'TOP', _('Top')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='specialist_profile')
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.NEW)
    rating = models.FloatField(default=0.0)
    is_verified = models.BooleanField(default=False)
    # Balance will be handled in Wallet app, but good to have a conceptual link? No, keep separate.
    
    def __str__(self):
        return f"Specialist {self.user.email} ({self.level})"

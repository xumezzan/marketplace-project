from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

class UserManager(BaseUserManager):
    """Custom user manager where phone_number is the unique identifiers
    for authentication instead of usernames."""
    
    def create_user(self, phone_number, password=None, **extra_fields):
        """Create and save a User with the given phone number and password."""
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Create and save a SuperUser with the given phone number and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """Custom User model using phone number as the primary identifier."""
    
    class Role(models.TextChoices):
        CLIENT = 'client', _('Client')
        SPECIALIST = 'specialist', _('Specialist')
        ADMIN = 'admin', _('Admin')

    username = None  # Remove username field
    phone_number = PhoneNumberField(_('phone number'), unique=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    telegram_chat_id = models.CharField(_('telegram chat id'), max_length=100, blank=True, null=True, unique=True)
    role = models.CharField(
        _('role'), 
        max_length=20, 
        choices=Role.choices, 
        default=Role.CLIENT
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []  # Email is not required

    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)


class ClientProfile(models.Model):
    """Profile for customers/clients."""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_profile'
    )
    full_name = models.CharField(_('full name'), max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    
    def __str__(self):
        return f"Client: {self.user.phone_number}"


class SpecialistProfile(models.Model):
    """Profile for service providers/specialists."""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='specialist_profile'
    )
    bio = models.TextField(_('bio'), blank=True)
    rating = models.FloatField(_('rating'), default=0.0)
    review_count = models.IntegerField(_('review count'), default=0)
    is_verified = models.BooleanField(_('verified'), default=False)
    telegram_username = models.CharField(_('telegram username'), max_length=100, blank=True)
    portfolio_links = models.JSONField(_('portfolio links'), default=list, blank=True)
    location = models.PointField(_('location'), null=True, blank=True)
    categories = models.ManyToManyField(
        'services.Category',
        related_name='specialists',
        verbose_name=_('categories'),
        blank=True
    )
    
    def __str__(self):
        return f"Specialist: {self.user.phone_number}"

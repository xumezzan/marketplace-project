from django.db import models
from django.conf import settings
from apps.requests.models import Request
from django.utils.translation import gettext_lazy as _

class Deal(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    request = models.OneToOneField(Request, on_delete=models.PROTECT, related_name='deal')
    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='deals')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)

    # Mutual Consent for Contacts
    client_requested_contacts = models.BooleanField(default=False)
    specialist_approved_contacts = models.BooleanField(default=False)
    contacts_shared_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Deal {self.id}: {self.request} -> {self.specialist}"

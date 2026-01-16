from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class VerificationDocument(models.Model):
    class Type(models.TextChoices):
        PASSPORT = 'PASSPORT', _('Passport')
        DIPLOMA = 'DIPLOMA', _('Diploma')
        LICENSE = 'LICENSE', _('License')
        CERTIFICATE = 'CERTIFICATE', _('Certificate')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification_documents')
    document_type = models.CharField(max_length=20, choices=Type.choices)
    file = models.FileField(upload_to='verification_docs/')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_docs'
    )

    def __str__(self):
        return f"{self.specialist} - {self.document_type} ({self.status})"

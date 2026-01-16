from django.contrib import admin
from .models import VerificationDocument

@admin.register(VerificationDocument)
class VerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'document_type', 'status', 'uploaded_at')
    list_filter = ('status', 'document_type')
    actions = ['approve_docs', 'reject_docs']

    def approve_docs(self, request, queryset):
        queryset.update(status='APPROVED', reviewed_at=request.user)
    approve_docs.short_description = "Approve selected documents"
    
    def reject_docs(self, request, queryset):
        queryset.update(status='REJECTED', reviewed_at=request.user)

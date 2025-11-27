from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import User, ClientProfile, SpecialistProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ('phone_number', 'role', 'is_active', 'is_staff')
    search_fields = ('phone_number', 'email')
    ordering = ('phone_number',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('email', 'role', 'telegram_chat_id')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(SpecialistProfile)
class SpecialistProfileAdmin(ModelAdmin):
    list_display = ('get_phone', 'rating', 'review_count', 'is_verified', 'telegram_username')
    list_filter = ('is_verified', 'rating')
    search_fields = ('user__phone_number', 'telegram_username')
    actions = ['verify_specialists', 'unverify_specialists']

    def get_phone(self, obj):
        return obj.user.phone_number
    get_phone.short_description = _('Phone Number')

    @admin.action(description=_('Verify selected specialists'))
    def verify_specialists(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, _("Selected specialists have been verified."))

    @admin.action(description=_('Unverify selected specialists'))
    def unverify_specialists(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, _("Selected specialists have been unverified."))

@admin.register(ClientProfile)
class ClientProfileAdmin(ModelAdmin):
    list_display = ('user', 'full_name', 'city')
    search_fields = ('user__phone_number', 'full_name', 'city')

from django.contrib import admin
from .models import Gift


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient_name", "sender_name", "created_at", "expires_at", "view_count", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("id", "recipient_name", "sender_name")
    readonly_fields = ("id", "created_at", "view_count")

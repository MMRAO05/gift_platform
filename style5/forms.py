from django import forms
from .models import Gift


class GiftForm(forms.ModelForm):
    """Used by the admin / any server-rendered fallback form for style5."""

    class Meta:
        model = Gift
        fields = ["sender_name", "recipient_name", "passkey", "data", "expires_at", "is_active"]

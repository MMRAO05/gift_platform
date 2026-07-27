from django import forms
from .models import Gift


class GiftForm(forms.ModelForm):
    class Meta:
        model = Gift
        fields = ["sender_name", "recipient_name", "short_line", "letter", "passkey", "data", "expires_at", "is_active"]

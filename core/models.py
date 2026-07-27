import uuid
import random
import string
from django.db import models
from django.utils import timezone


def generate_short_code():
    """Generate a random short code (10-15 characters) with numbers only."""
    chars = string.digits
    length = random.randint(10, 15)
    return ''.join(random.choice(chars) for _ in range(length))


class BaseGift(models.Model):
    """
    Abstract base model shared by every style app.
    Each style (style1..style9, birthday, classic) gets its OWN concrete
    model + its own table + its own admin.py — but they all share this
    common structure so the shareable-link / passkey / expiry system
    behaves identically everywhere.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_code = models.CharField(max_length=15, unique=True, blank=True, null=True)

    sender_name = models.CharField(max_length=150, blank=True)
    recipient_name = models.CharField(max_length=150, blank=True)
    passkey = models.CharField(max_length=8, blank=True, default="")

    # The ENTIRE original client-side "state" object (name/letter/photos/
    # occasion/etc, whatever shape that specific template used) is stored
    # here as-is. This is what makes the bridge script generic: it just
    # forwards whatever JSON payload the page already built, untouched.
    data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient_name or 'Gift'} ({self.id})"

    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def register_view(self):
        type(self).objects.filter(pk=self.pk).update(view_count=models.F("view_count") + 1)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = generate_short_code()
            # Ensure uniqueness
            while type(self).objects.filter(short_code=self.short_code).exists():
                self.short_code = generate_short_code()
        super().save(*args, **kwargs)

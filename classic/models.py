from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Gift for the main "classic" builder (index.html) — the one with a
    real create/load/verify REST contract already designed into its JS."""

    short_line = models.CharField(max_length=300, blank=True)
    letter = models.TextField(blank=True)

    class Meta:
        verbose_name = "Classic Gift"
        verbose_name_plural = "Classic Gifts"

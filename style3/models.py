from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Shareable gift for the "style3" template (3.html)."""

    class Meta:
        verbose_name = "Style3 Gift"
        verbose_name_plural = "Style3 Gifts"

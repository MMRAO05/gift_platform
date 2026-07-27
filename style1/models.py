from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Shareable gift for the "style1" template (1.html)."""

    class Meta:
        verbose_name = "Style1 Gift"
        verbose_name_plural = "Style1 Gifts"

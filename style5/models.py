from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Shareable gift for the "style5" template (5.html)."""

    class Meta:
        verbose_name = "Style5 Gift"
        verbose_name_plural = "Style5 Gifts"

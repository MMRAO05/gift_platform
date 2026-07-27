from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Shareable gift for the "style9" template (9.html)."""

    class Meta:
        verbose_name = "Style9 Gift"
        verbose_name_plural = "Style9 Gifts"

from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Shareable gift for the "style7" template (7.html)."""

    class Meta:
        verbose_name = "Style7 Gift"
        verbose_name_plural = "Style7 Gifts"

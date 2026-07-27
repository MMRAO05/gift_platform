from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Shareable gift for the "style4" template (4.html)."""

    class Meta:
        verbose_name = "Style4 Gift"
        verbose_name_plural = "Style4 Gifts"

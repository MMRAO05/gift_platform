from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Shareable gift for the "style2" template (2.html)."""

    class Meta:
        verbose_name = "Style2 Gift"
        verbose_name_plural = "Style2 Gifts"

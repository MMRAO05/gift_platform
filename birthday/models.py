from django.db import models
from core.models import BaseGift


class Gift(BaseGift):
    """Shareable gift for the "birthday" template (birthday.html)."""

    class Meta:
        verbose_name = "Birthday Gift"
        verbose_name_plural = "Birthday Gifts"

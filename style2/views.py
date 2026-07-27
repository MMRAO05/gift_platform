import json
from django.shortcuts import render
from django.views import View
from core.generic_views import BaseSaveGiftAPIView
from .models import Gift

STYLE_SLUG = "style2"


class CreatePageView(View):
    """Serves the original 2.html page unchanged (setup + reveal
    in one template, exactly like the source file)."""

    def get(self, request):
        return render(request, "style2/page.html")


class SaveGiftAPIView(BaseSaveGiftAPIView):
    model = Gift
    style_slug = STYLE_SLUG


class RevealSeedView(View):
    """/style2/g/<short_code>/  — looks the gift up, then serves a tiny page
    that re-creates the EXACT url format (query) the original page
    already knows how to load from, so the real page code (unchanged)
    takes it from there."""

    def get(self, request, short_code):
        from django.shortcuts import get_object_or_404
        from django.http import Http404
        gift = get_object_or_404(Gift, short_code=short_code)
        if gift.is_expired or not gift.is_active:
            raise Http404("This gift link has expired.")
        gift.register_view()
        return render(request, "style2/seed_redirect.html", {
            "gift_json": json.dumps(gift.data),
            "gift_id": str(gift.id),
        })

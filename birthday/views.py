import json
from django.shortcuts import render
from django.views import View
from core.generic_views import BaseSaveGiftAPIView
from .models import Gift

STYLE_SLUG = "birthday"


class CreatePageView(View):
    """Serves the original birthday.html page unchanged (setup + reveal
    in one template, exactly like the source file)."""

    def get(self, request):
        return render(request, "birthday/page.html")


class SaveGiftAPIView(BaseSaveGiftAPIView):
    model = Gift
    style_slug = STYLE_SLUG


class RevealSeedView(View):
    """/birthday/g/<uuid>/  — window.__PRESET__ has to exist on the SAME
    page load as the main script (it's an in-memory JS global, it can't
    survive a redirect), so unlike the other styles this renders
    page.html directly with the gift JSON injected."""

    def get(self, request, gift_id):
        from django.shortcuts import get_object_or_404
        from django.http import Http404
        gift = get_object_or_404(Gift, pk=gift_id)
        if gift.is_expired or not gift.is_active:
            raise Http404("This gift link has expired.")
        gift.register_view()
        return render(request, "birthday/page.html", {
            "gift_json": json.dumps(gift.data),
        })

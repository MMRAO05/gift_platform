import json
import time
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Gift


class IndexPageView(View):
    """Serves index.html unchanged — it already contains its own setup
    screen AND its own JS for loading a gift by ?id=, so ONE template
    handles both creating and viewing a gift, exactly as designed."""

    def get(self, request):
        return render(request, "classic/index.html")


@method_decorator(csrf_exempt, name="dispatch")
class GiftAPIView(View):
    """
    Matches the REST contract the page's own JS already expects:
      POST /api/gift            -> {giftId}
      GET  /api/gift/<id>       -> full gift JSON (name, shortLine, letter,
                                    passkey, photos, createdAt, expiresIn)
      POST /api/gift/<id>/verify -> {passkey} -> {success}
    """

    verify = False

    def post(self, request, gift_id=None, verify=False):
        if self.verify:
            return self._verify(request, gift_id)
        return self._create(request)

    def get(self, request, gift_id=None, verify=False):
        return self._retrieve(request, gift_id)

    def _create(self, request):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        gift = Gift.objects.create(
            recipient_name=payload.get("name", "")[:150],
            short_line=payload.get("shortLine", ""),
            letter=payload.get("letter", ""),
            passkey=str(payload.get("passkey", "8274"))[:8],
            data=payload,
        )
        return JsonResponse({"success": True, "giftId": str(gift.id)})

    def _retrieve(self, request, gift_id):
        gift = get_object_or_404(Gift, pk=gift_id)
        gift.register_view()
        payload = dict(gift.data or {})
        # Always answer from the stored payload so createdAt/expiresIn
        # (client-side expiry check) match exactly what was saved.
        payload.setdefault("name", gift.recipient_name)
        payload.setdefault("shortLine", gift.short_line)
        payload.setdefault("letter", gift.letter)
        payload.setdefault("passkey", gift.passkey or "8274")
        payload["id"] = str(gift.id)
        return JsonResponse(payload)

    def _verify(self, request, gift_id):
        gift = get_object_or_404(Gift, pk=gift_id)
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        entered = str(payload.get("passkey", ""))
        stored = gift.passkey or (gift.data or {}).get("passkey", "8274")
        if entered == str(stored):
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Incorrect passkey"}, status=403)

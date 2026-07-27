import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class BaseSaveGiftAPIView(View):
    """
    POST endpoint: receives whatever JSON "state" the template's bridge
    script collected (name, letter, photos, passkey, occasion...) and
    stores it as one Gift row. Returns {id, url} used to build the real
    shareable link (/<style>/g/<id>/).

    Subclass per style app and set `model`.
    """
    model = None
    expiry_hours = 24 * 7  # default 7 days, override per style if needed

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        gift = self.model.objects.create(
            sender_name=payload.get("senderName", "") or payload.get("from", ""),
            recipient_name=payload.get("name", "") or payload.get("recipient", ""),
            passkey=str(payload.get("passkey", ""))[:8],
            data=payload,
            expires_at=timezone.now() + timezone.timedelta(hours=self.expiry_hours),
        )
        return JsonResponse({
            "success": True,
            "id": str(gift.id),
            "short_code": gift.short_code,
            "url": request.build_absolute_uri(f"/{self.style_slug}/g/{gift.short_code}/"),
        })


class BaseVerifyPasskeyAPIView(View):
    model = None

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, gift_id, *args, **kwargs):
        gift = get_object_or_404(self.model, pk=gift_id)
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        entered = str(payload.get("passkey", ""))
        stored = gift.passkey or (gift.data or {}).get("passkey", "")
        if not stored or entered == str(stored):
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Incorrect passkey"}, status=403)


class BaseGiftJSONAPIView(View):
    """GET endpoint returning the stored JSON — used only as a fallback."""
    model = None

    def get(self, request, gift_id, *args, **kwargs):
        gift = get_object_or_404(self.model, pk=gift_id)
        if gift.is_expired or not gift.is_active:
            return JsonResponse({"error": "This gift link has expired."}, status=410)
        gift.register_view()
        return JsonResponse(gift.data)

from django.urls import path
from . import views

app_name = "classic"

urlpatterns = [
    path("", views.IndexPageView.as_view(), name="index"),
]

api_urlpatterns = [
    path("gift", views.GiftAPIView.as_view(), name="gift-create"),
    path("gift/<uuid:gift_id>", views.GiftAPIView.as_view(), name="gift-detail"),
    path("gift/<uuid:gift_id>/verify", views.GiftAPIView.as_view(verify=True), name="gift-verify"),
]

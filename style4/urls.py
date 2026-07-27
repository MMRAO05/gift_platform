from django.urls import path
from . import views

app_name = "style4"

urlpatterns = [
    path("", views.CreatePageView.as_view(), name="create"),
    path("g/<uuid:gift_id>/", views.RevealSeedView.as_view(), name="reveal"),
]

api_urlpatterns = [
    path("save/", views.SaveGiftAPIView.as_view(), name="save"),
]

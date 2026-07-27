from django.urls import path
from . import views

app_name = "style5"

urlpatterns = [
    path("", views.CreatePageView.as_view(), name="create"),
    path("g/<str:short_code>/", views.RevealSeedView.as_view(), name="reveal"),
]

api_urlpatterns = [
    path("save/", views.SaveGiftAPIView.as_view(), name="save"),
]

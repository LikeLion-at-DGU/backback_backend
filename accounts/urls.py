from django.urls import path, include
from rest_framework import routers
from .views import *
from . import views

app_name = "accounts"

profile_router = routers.SimpleRouter(trailing_slash=False)
profile_router.register("profiles", ProfileViewSet, basename="profiles")

urlpatterns = [
    path("", include(profile_router.urls)),
    path("me/", MeViewSet.as_view(), name="me"),
    path("accounts/google/login/", google_login, name="google_login"),
    path("accounts/google/login/callback/", google_callback, name="google_callback"),
    path(
        "accounts/google/login/finish/",
        GoogleLogin.as_view(),
        name="google_login_todjango",
    ),
    path("accounts/kakao/login/", views.kakao_login, name="kakao_login"),
    path("accounts/kakao/login/callback/", views.kakao_callback, name="kakao_callback"),
    path(
        "accounts/kakao/login/finish/",
        views.KakaoLogin.as_view(),
        name="kakao_login_todjango",
    ),
]

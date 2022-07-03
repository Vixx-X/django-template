from django.urls.conf import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

router = routers.DefaultRouter()
router.register(
    r"users",
    views.UserViewSet,
)

user_urls = [
    path(
        "register/",
        views.RegistrationView.as_view(),
        name="register",
    ),
    path(
        "profile/",
        views.ProfileView.as_view(),
        name="profile",
    ),
    path(
        "password-reset/",
        views.PasswordResetView.as_view(),
        name="password-reset",
    ),
    path(
        "password-reset/confirm/<str:uidb64>/<str:token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "change-password/",
        views.ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "change-email/",
        views.ChangeEmailView.as_view(),
        name="change-email",
    ),
    path(
        "generate-otp/",
        views.SendOTPView.as_view(),
        name="generate-otp",
    ),
]

auth_urls = [
    path(
        "",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "verify/",
        TokenVerifyView.as_view(),
        name="token_verify",
    ),
]

urlpatterns = [
    path(
        "user/",
        include(user_urls),
    ),
    path(
        "token/",
        include(auth_urls),
    ),
    path(
        "",
        include(router.urls),
    ),
]

""" back URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.base import View

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def apidocs_view_permission(user):
    "User can read or se the api documentation if it is staff"
    return user.is_staff or True


docs_urls = [
    # documentation
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # optional ui:
    path(
        "",
        user_passes_test(apidocs_view_permission)(
            SpectacularSwaggerView.as_view(url_name="schema")
        ),
        name="default-docs",
    ),
    path(
        "swagger-ui/",
        user_passes_test(apidocs_view_permission)(
            SpectacularSwaggerView.as_view(url_name="schema")
        ),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        user_passes_test(apidocs_view_permission)(
            SpectacularRedocView.as_view(url_name="schema")
        ),
        name="redoc",
    ),
]


urlpatterns = (
    [
        # admin
        path("admin/", admin.site.urls),
        # user
        path(
            "",
            include(
                ("back.apps.user.urls", "back.apps.user"), namespace="user"
            ),
        ),
        # docs
        path("docs/", include(docs_urls)),
        # misc
        path(
            "user/password-reset/confirm/<str:uidb64>/<str:token>/",
            View.as_view(),
            name="password-reset-confirm",
        ),
        path(
            "user/email-settings/<str:uidb64>/<str:token>/",
            View.as_view(),
            name="email-settings",
        ),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

# handler400 = 'back.core.exception_handler.bad_request'
# handler403 = 'back.core.exception_handler.default_handler'
# handler404 = 'back.core.exception_handler.default_handler'
# handler500 = 'back.core.exception_handler.default_handler'
# handler500 = 'rest_framework.exceptions.server_error'

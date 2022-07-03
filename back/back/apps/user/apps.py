from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UserConfig(AppConfig):
    name = "back.apps.user"
    label = "user"
    verbose_name = _("user")

    def ready(self):
        from . import signals
        return super().ready()

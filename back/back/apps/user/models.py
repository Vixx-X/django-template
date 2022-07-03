from django.core import validators
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django_otp.plugins.otp_email.models import EmailDevice as BaseEmailDevice

from back.apps.user.mails import SendOTPMail


class User(AbstractUser):
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    document_id = models.CharField(
        _("document id (cedula/rif)"),
        max_length=15,
        validators=[
            validators.RegexValidator(
                regex=r"^[eEvVjJ]\d+$",
                message=_("your document id is not well formatted"),
            ),
        ],
    )

    def get_full_name(self):
        # Returns the first_name and the last_name
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return self.get_full_name()

    def get_short_name(self):
        # Returns the short name for the user.
        return self.first_name

    def get_pretty_document(self):
        # Returns document_id prettier
        document_id = str(self.document_id)
        letter = document_id[:1].upper()
        number = document_id[1:]
        return f"{letter}-{number}"

    @property
    def document(self):
        return self.get_pretty_document()


class EmailDevice(BaseEmailDevice):
    """
    A :class:`~django_otp.models.SideChannelDevice` that delivers a token to
    the email address saved in this object or alternatively to the user's
    registered email address (``user.email``).
    The tokens are valid for :setting:`OTP_EMAIL_TOKEN_VALIDITY` seconds. Once
    a token has been accepted, it is no longer valid.
    Note that if you allow users to reset their passwords by email, this may
    provide little additional account security. It may still be useful for,
    e.g., requiring the user to re-verify their email address on new devices.
    .. attribute:: email
        *EmailField*: An alternative email address to send the tokens to.
    """

    class Meta:
        proxy = True

    def generate_challenge(self, extra_context=None):
        """
        Generates a random token and emails it to the user.

        :param extra_context: Additional context variables for rendering the
            email template.
        :type extra_context: dict

        """
        self.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY)

        context = {'token': self.token, **(extra_context or {})}

        mail = SendOTPMail()
        mail.set_context(**context)
        mail.send([self.user.email])

        message = _("sent by email")

        return message

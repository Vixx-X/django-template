from datetime import timedelta

from rest_framework import generics, serializers, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema, inline_serializer

from django_otp import devices_for_user
from rest_framework.views import APIView

from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    PasswordResetSerializer,
    PasswordSerializer,
    OTPRequestSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    RegisterUserSerializer,
)

from .models import User


class UserViewSet(viewsets.ModelViewSet):
    """
    Entrypoint for users
    """

    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileView(generics.RetrieveAPIView):
    """
    Get data for current user
    """

    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class PasswordResetView(generics.GenericAPIView):
    token_generator = default_token_generator
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        opts = {
            "request": self.request,
        }
        serializer.save(**opts)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PasswordResetConfirmView(generics.GenericAPIView):
    token_generator = default_token_generator
    serializer_class = PasswordSerializer

    # drf-spectacular will not call get_serializer if is not overrided
    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)

    def get_object(self):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(self.kwargs["uidb64"]).decode()
            user = User._default_manager.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            return None

        if not self.token_generator.check_token(user, self.kwargs["token"]):
            return None
        return user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object is None:
            return Response(
                {"invalid_link": self.object is None}, status=status.HTTP_410_GONE
            )
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": _(
                    "Your password have been successfully changed. Please sign in with your new credentials."
                )
            }
        )

    @extend_schema(
        responses=inline_serializer(
            "invalid_link",
            {
                "invalid_link": serializers.BooleanField(),
            },
        ),
    )
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = {"invalid_link": self.object is None}
        if self.object is None:
            return Response(data, status=status.HTTP_410_GONE)
        return Response(data)


class SendOTPView(generics.GenericAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = OTPRequestSerializer

    def post(self, request, *args, **kwargs):
        user = request.user

        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.data
        devices = devices_for_user(user=user, confirmed=True, for_verify=True)
        if not devices:
            return Response(
                {"message": _("Please contact customer service")},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        device = next(devices)

        email = data.get("email")
        if email:
            device.email = email
        else:
            data["email"] = user.email

        extra_context = {"user":user}  # this is de ctx of the OTP mail

        data["device"] = device.persistent_id

        seconds = int(settings.OTP_EMAIL_TOKEN_VALIDITY)
        data["expire"] = (now() + timedelta(seconds=seconds)).isoformat()

        data["message"] = device.generate_challenge(extra_context)

        return Response(data, status=status.HTTP_201_CREATED)


class ChangePasswordView(generics.GenericAPIView):
    """
    Change password endpoint
    """

    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    # drf-spectacular will not call get_serializer if is not overrided
    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": _("Your password have been successfully changed.")})


class ChangeEmailView(generics.GenericAPIView):
    """
    Change email endpoint
    """

    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    serializer_class = ChangeEmailSerializer
    permission_classes = (IsAuthenticated,)

    # drf-spectacular will not call get_serializer if is not overrided
    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": _("Your email have been successfully changed.")})


class RegistrationView(generics.GenericAPIView):
    """
    API for registering users

    Will create a new user when the user with the specific email does
    not exist (HTTP_201_CREATED).

    It won't login the newly created user, You can do this with the token API.
    """

    serializer_class = RegisterUserSerializer

    def send_registration_email(self, user):
        pass

    def post(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request.data)

        ser.is_valid(raise_exception=True)

        # create the user
        user = ser.save()
        self.send_registration_email(user)
        return Response(
            {"message": _("You have successfully registered.")},
            status=status.HTTP_201_CREATED,
        )

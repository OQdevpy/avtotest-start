from datetime import timedelta

from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from apps.accounts.models import DeviceSession, hash_secret

from .crypto import unwrap_key

KEYWORD = "Bin"


class DeviceSessionAuthentication(BaseAuthentication):
    """`Authorization: Bin <token>` + `X-Device-Id`.

    Token o'g'irlansa ham boshqa qurilmada ishlamaydi: device_id mos kelishi va
    so'rov tanasi faqat shu sessiyaning AES kaliti bilan ochilishi kerak.
    """

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith(KEYWORD + " "):
            return None
        token = header[len(KEYWORD) + 1:].strip()
        if not token or len(token) > 128:
            raise exceptions.AuthenticationFailed("invalid_token")
        try:
            session = DeviceSession.objects.select_related("student").get(token_hash=hash_secret(token))
        except DeviceSession.DoesNotExist:
            raise exceptions.AuthenticationFailed("invalid_token")
        if not session.is_valid:
            raise exceptions.AuthenticationFailed("session_expired")
        if request.META.get("HTTP_X_DEVICE_ID", "") != session.device_id:
            raise exceptions.AuthenticationFailed("device_mismatch")

        now = timezone.now()
        if now - session.last_seen > timedelta(minutes=1):
            DeviceSession.objects.filter(pk=session.pk).update(last_seen=now)
        session.key = unwrap_key(bytes(session.wrapped_key), session.sid)
        return session.student, session

    def authenticate_header(self, request):
        return KEYWORD

import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from binproto.crypto import BinError, b64d, b64e, handshake, wrap_key

from .models import DeviceSession, LoginFailure, Student, hash_secret, new_sid, normalize_code

log = logging.getLogger("security")


def client_ip(request):
    # nginx X-Real-IP ni o'zi qo'yadi; mijoz yuborgan X-Forwarded-For'ga ishonilmaydi.
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR")


class LoginSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=32)
    device_id = serializers.RegexField(r"^[A-Za-z0-9_-]{16,64}$")
    client_pub = serializers.CharField(max_length=128)  # base64, 65 bayt


class LoginView(APIView):
    """Kirish kodi + ECDH handshake. Javobda AES kaliti YO'Q — faqat serverning
    ochiq kaliti va salt; kalitni brauzer o'zi hisoblaydi."""

    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ip = client_ip(request)

        window = timezone.now() - timedelta(minutes=15)
        if LoginFailure.objects.filter(ip=ip, created_at__gte=window).count() >= settings.LOGIN_MAX_FAILS:
            return Response({"error": "too_many_attempts"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        code = normalize_code(ser.validated_data["code"])
        student = Student.objects.filter(code_hash=hash_secret(code)).first() if code else None
        if student is None or not student.can_login():
            LoginFailure.objects.create(ip=ip)
            log.info("login failed ip=%s", ip)
            # Kod mavjud-yo'qligini oshkor qilmaslik uchun bitta umumiy xato.
            return Response({"error": "invalid_code"}, status=status.HTTP_401_UNAUTHORIZED)

        device_id = ser.validated_data["device_id"]
        sid = new_sid()
        try:
            key, server_pub, salt = handshake(b64d(ser.validated_data["client_pub"]), sid)
        except (BinError, ValueError):
            return Response({"error": "bad_public_key"}, status=status.HTTP_400_BAD_REQUEST)

        token = secrets.token_urlsafe(32)
        with transaction.atomic():
            Student.objects.select_for_update().filter(pk=student.pk).first()
            active = student.sessions.filter(revoked=False, expires_at__gt=timezone.now())
            # Shu qurilmaning eski sessiyalari almashtiriladi.
            active.filter(device_id=device_id).update(revoked=True)
            if active.exclude(device_id=device_id).count() >= student.max_devices:
                log.info("device limit student=%s ip=%s", student.pk, ip)
                return Response({"error": "device_limit"}, status=status.HTTP_403_FORBIDDEN)
            session = DeviceSession.objects.create(
                sid=sid, student=student, token_hash=hash_secret(token), device_id=device_id,
                wrapped_key=wrap_key(key, sid), ip=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
                expires_at=timezone.now() + settings.BIN_SESSION_TTL,
            )
        log.info("login ok student=%s sid=%s ip=%s", student.pk, sid, ip)
        return Response({
            "token": token,
            "sid": sid,
            "server_pub": b64e(server_pub),
            "salt": b64e(salt),
            "expires_at": session.expires_at.isoformat(),
            "student": {"full_name": student.full_name},
        })


class LogoutView(APIView):
    def post(self, request):
        DeviceSession.objects.filter(pk=request.auth.pk).update(revoked=True)
        return Response({"ok": True})


class MeView(APIView):
    def get(self, request):
        s = request.user
        return Response({
            "full_name": s.full_name,
            "expires_at": s.expires_at.isoformat() if s.expires_at else None,
            "session_expires_at": request.auth.expires_at.isoformat(),
        })

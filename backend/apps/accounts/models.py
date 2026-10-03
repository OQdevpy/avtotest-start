import hashlib
import hmac
import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # chalkash belgilar (O/0, I/1) yo'q


def hash_secret(value):
    """Kod va tokenlar faqat HMAC ko'rinishida saqlanadi — baza o'g'irlansa ham ochilmaydi."""
    return hmac.new(settings.SECRET_KEY.encode(), value.encode(), hashlib.sha256).hexdigest()


def normalize_code(code):
    return "".join(ch for ch in code.upper() if ch.isalnum())


def new_sid():
    return uuid.uuid4().hex


def generate_code(length=12):
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(length))


class Student(models.Model):
    """O'quvchi. Shef (admin) kirish kodini beradi; parol yo'q."""

    full_name = models.CharField("F.I.Sh.", max_length=150)
    phone = models.CharField("Telefon", max_length=20, blank=True)
    code_hash = models.CharField(max_length=64, unique=True, editable=False)
    code_hint = models.CharField("Kod (oxirgi 4 belgi)", max_length=8, editable=False)
    is_active = models.BooleanField("Faol", default=True)
    expires_at = models.DateTimeField("Amal qilish muddati", null=True, blank=True)
    max_devices = models.PositiveSmallIntegerField("Qurilmalar soni", default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "O'quvchi"
        verbose_name_plural = "O'quvchilar"

    def __str__(self):
        return f"{self.full_name} (…{self.code_hint})"

    # DRF IsAuthenticated uchun
    is_authenticated = True

    def set_code(self, code):
        code = normalize_code(code)
        self.code_hash = hash_secret(code)
        self.code_hint = code[-4:]

    def can_login(self):
        return self.is_active and (self.expires_at is None or self.expires_at > timezone.now())


class DeviceSession(models.Model):
    """Bitta qurilmadagi kirish. ECDH bilan kelishilgan AES kaliti shu yerda (o'ralgan holda)."""

    sid = models.CharField(max_length=32, unique=True, default=new_sid, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sessions")
    token_hash = models.CharField(max_length=64, unique=True)
    device_id = models.CharField(max_length=64)
    wrapped_key = models.BinaryField()
    user_agent = models.CharField(max_length=255, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Qurilma sessiyasi"
        verbose_name_plural = "Qurilma sessiyalari"
        indexes = [models.Index(fields=["student", "revoked"])]

    def __str__(self):
        return f"{self.student} · {self.device_id[:8]}"

    @property
    def is_valid(self):
        return not self.revoked and self.expires_at > timezone.now() and self.student.can_login()


class LoginFailure(models.Model):
    """Noto'g'ri kod urinishlari — IP bo'yicha bloklash uchun."""

    ip = models.GenericIPAddressField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

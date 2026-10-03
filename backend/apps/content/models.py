"""Kontent: bosqich → bo'lim → savol → javob; variantlar (biletlar).

Har bir matn uch tilda: uz (lotin), kr (o'zbek kirill), ru.
"""
import uuid

from django.core.validators import FileExtensionValidator
from django.db import models

LANGS = ("uz", "kr", "ru")
IMAGE_EXT = FileExtensionValidator(["png", "jpg", "jpeg", "webp", "gif", "svg"])
AUDIO_EXT = FileExtensionValidator(["mp3", "ogg", "m4a", "wav"])


def upload_to(instance, filename):
    # Asl fayl nomi saqlanmaydi — yo'lni taxmin qilib bo'lmaydi.
    ext = filename.rsplit(".", 1)[-1].lower()[:5]
    return f"{instance._meta.model_name}/{uuid.uuid4().hex}.{ext}"


def i18n(prefix, verbose, blank=False, text=False):
    field = models.TextField if text else models.CharField
    kw = {} if text else {"max_length": 500}
    return {
        f"{prefix}_{lang}": field(f"{verbose} ({lang})", blank=blank or lang != "uz", **kw)
        for lang in LANGS
    }


class I18nMixin:
    def tr(self, prefix, lang):
        """Tanlangan til bo'sh bo'lsa uz → ru → kr tartibida zaxiraga tushadi."""
        for code in (lang, "uz", "ru", "kr"):
            value = getattr(self, f"{prefix}_{code}", "")
            if value:
                return value
        return ""


class Stage(I18nMixin, models.Model):
    number = models.PositiveSmallIntegerField("Raqam", unique=True)
    locals().update(i18n("title", "Nomi", blank=True))

    class Meta:
        ordering = ["number"]
        verbose_name = "Bosqich"
        verbose_name_plural = "Bosqichlar"

    def __str__(self):
        return f"{self.number}-bosqich"


class Category(I18nMixin, models.Model):
    """Bo'lim (masalan, «Ogohlantiruvchi belgilar»)."""

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="categories", verbose_name="Bosqich")
    locals().update(i18n("title", "Nomi"))
    locals().update(i18n("info", "Ma'lumot matni", blank=True, text=True))
    icon = models.FileField("Belgi rasmi", upload_to=upload_to, blank=True, validators=[IMAGE_EXT])
    info_image = models.FileField("Ma'lumot rasmi", upload_to=upload_to, blank=True, validators=[IMAGE_EXT])
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["stage__number", "order", "id"]
        verbose_name = "Bo'lim"
        verbose_name_plural = "Bo'limlar"

    def __str__(self):
        return f"{self.stage.number} · {self.title_uz}"


class Question(I18nMixin, models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="questions", verbose_name="Bo'lim")
    locals().update(i18n("text", "Savol", text=True))
    locals().update(i18n("explanation", "Izoh", blank=True, text=True))
    image = models.FileField("Rasm", upload_to=upload_to, blank=True, validators=[IMAGE_EXT])
    photo_hint = models.FileField("Photo izoh", upload_to=upload_to, blank=True, validators=[IMAGE_EXT])
    audio_hint = models.FileField("Audio izoh", upload_to=upload_to, blank=True, validators=[AUDIO_EXT])
    order = models.PositiveIntegerField("Tartib", default=0)
    is_published = models.BooleanField("Nashr etilgan", default=True)

    class Meta:
        ordering = ["category", "order", "id"]
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"

    def __str__(self):
        return self.text_uz[:80]


class Answer(I18nMixin, models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    locals().update(i18n("text", "Javob", text=True))
    is_correct = models.BooleanField("To'g'ri", default=False)
    order = models.PositiveSmallIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"

    def __str__(self):
        return self.text_uz[:60]


class Variant(models.Model):
    """Test varianti. stage bo'sh bo'lsa — umumiy «Test variantlari» (1..60),
    aks holda «Bo'lim bo'yicha test variantlari» ichidagi bosqich varianti."""

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True, blank=True,
                              related_name="variants", verbose_name="Bosqich")
    number = models.PositiveSmallIntegerField("Raqam")
    questions = models.ManyToManyField(Question, through="VariantQuestion", related_name="variants")

    class Meta:
        ordering = ["stage__number", "number"]
        constraints = [
            models.UniqueConstraint(fields=["stage", "number"], name="uniq_stage_variant"),
            models.UniqueConstraint(fields=["number"], condition=models.Q(stage__isnull=True),
                                    name="uniq_general_variant"),
        ]
        verbose_name = "Variant"
        verbose_name_plural = "Variantlar"

    def __str__(self):
        return f"{self.stage or 'Umumiy'} · {self.number}-variant"


class VariantQuestion(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        unique_together = [("variant", "question")]

from django.db import models
from django.utils import timezone

from apps.accounts.models import Student
from apps.content.models import Answer, Question


class Attempt(models.Model):
    class Kind(models.TextChoices):
        STUDY = "study", "Ta'lim (bo'lim)"
        CATEGORY = "category", "Qism bo'yicha test"
        STAGE = "stage", "Bosqichli test"
        FINAL = "final", "Yakuniy test"
        VARIANT = "variant", "Test varianti"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attempts")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    ref_id = models.PositiveIntegerField(null=True, blank=True)  # bo'lim / bosqich / variant id
    started_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)  # study rejimida yo'q
    finished_at = models.DateTimeField(null=True, blank=True)
    total = models.PositiveSmallIntegerField(default=0)
    correct = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Urinish"
        verbose_name_plural = "Urinishlar"

    def __str__(self):
        return f"{self.student} · {self.get_kind_display()} · {self.correct}/{self.total}"

    @property
    def is_open(self):
        return self.finished_at is None and (self.deadline is None or self.deadline > timezone.now())


class AttemptItem(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="items")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()
    # Javoblar tartibi aralashtiriladi — F1..F5 ni yod olib bo'lmaydi.
    answer_order = models.JSONField(default=list)
    chosen = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    is_correct = models.BooleanField(null=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position"]
        unique_together = [("attempt", "position"), ("attempt", "question")]

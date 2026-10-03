import random

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Answer, Category, Question, Stage, Variant
from apps.content.serializers import media_path, tri

from .models import Attempt, AttemptItem

Kind = Attempt.Kind


class StartSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=Kind.choices)
    ref = serializers.IntegerField(required=False, min_value=1)
    count = serializers.ChoiceField(choices=[20, 50], required=False, default=20)


def pick_questions(kind, ref, count):
    qs = Question.objects.filter(is_published=True)
    if kind in (Kind.STUDY, Kind.CATEGORY):
        category = get_object_or_404(Category, pk=ref)
        return list(qs.filter(category=category)), category.pk
    if kind == Kind.VARIANT:
        variant = get_object_or_404(Variant, pk=ref)
        return [vq.question for vq in variant.variantquestion_set.select_related("question")
                if vq.question.is_published], variant.pk
    if kind == Kind.STAGE:
        stage = get_object_or_404(Stage, pk=ref)
        qs, ref_id = qs.filter(category__stage=stage), stage.pk
    else:  # FINAL
        ref_id = None
    ids = list(qs.values_list("id", flat=True))
    chosen = random.SystemRandom().sample(ids, min(count, len(ids)))
    by_id = Question.objects.in_bulk(chosen)
    return [by_id[i] for i in chosen], ref_id


def serialize_attempt(attempt):
    """Savollar uchala tilda. To'g'ri javob faqat:
    - Ta'lim (study) rejimida, yoki
    - savolga javob berilgandan keyin (javob qulflangan, o'zgartirib bo'lmaydi), yoki
    - urinish yakunlangandan keyin qaytariladi."""
    items = list(attempt.items.select_related("question").prefetch_related("question__answers"))
    reveal_all = attempt.kind == Kind.STUDY or not attempt.is_open
    questions = []
    for it in items:
        q = it.question
        answers = {a.id: a for a in q.answers.all()}
        order = [i for i in it.answer_order if i in answers] or list(answers)
        correct_id = next((a.id for a in answers.values() if a.is_correct), None)
        show = reveal_all or it.chosen_id is not None
        questions.append({
            "id": q.id,
            "text": tri(q, "text"),
            "image": media_path("question", q, "image"),
            "photo_hint": media_path("question", q, "photo_hint") if show else None,
            "audio_hint": media_path("question", q, "audio_hint") if show else None,
            "explanation": tri(q, "explanation") if show else None,
            "answers": [{"id": answers[i].id, "text": tri(answers[i], "text")} for i in order],
            "chosen": it.chosen_id,
            "correct": correct_id if show else None,
        })
    now = timezone.now()
    return {
        "id": attempt.id,
        "kind": attempt.kind,
        "ref": attempt.ref_id,
        "finished": not attempt.is_open,
        "remaining": max(0, int((attempt.deadline - now).total_seconds())) if attempt.deadline else None,
        "questions": questions,
        "result": result_of(attempt) if not attempt.is_open else None,
    }


def result_of(attempt):
    mistakes = attempt.total - attempt.correct
    return {
        "total": attempt.total,
        "correct": attempt.correct,
        "mistakes": mistakes,
        # Rasmiy imtihon: 20 savolda ko'pi bilan 2 xato.
        "passed": mistakes <= max(2, attempt.total // 10),
    }


def finish(attempt):
    if attempt.finished_at is None:
        attempt.correct = attempt.items.filter(is_correct=True).count()
        attempt.finished_at = timezone.now()
        attempt.save(update_fields=["correct", "finished_at"])


class StartView(APIView):
    def post(self, request):
        ser = StartSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        kind, ref, count = (ser.validated_data.get(k) for k in ("kind", "ref", "count"))
        if kind != Kind.FINAL and ref is None:
            raise ValidationError({"ref": "required"})
        questions, ref_id = pick_questions(kind, ref, count)
        if not questions:
            return Response({"error": "empty"}, status=status.HTTP_404_NOT_FOUND)

        rng = random.SystemRandom()
        with transaction.atomic():
            attempt = Attempt.objects.create(
                student=request.user, kind=kind, ref_id=ref_id, total=len(questions),
                deadline=None if kind == Kind.STUDY else timezone.now() + settings.EXAM_DURATION,
            )
            items = []
            for pos, q in enumerate(questions, 1):
                order = [a.id for a in q.answers.all()]
                if settings.SHUFFLE_ANSWERS:
                    rng.shuffle(order)
                items.append(AttemptItem(attempt=attempt, question=q, position=pos, answer_order=order))
            AttemptItem.objects.bulk_create(items)
        return Response(serialize_attempt(attempt), status=status.HTTP_201_CREATED)


class AttemptView(APIView):
    def get(self, request, pk):
        attempt = get_object_or_404(Attempt, pk=pk, student=request.user)
        return Response(serialize_attempt(attempt))


class AnswerSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    answer = serializers.IntegerField()


class AnswerView(APIView):
    def post(self, request, pk):
        ser = AnswerSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        with transaction.atomic():
            attempt = get_object_or_404(Attempt.objects.select_for_update(), pk=pk, student=request.user)
            if attempt.kind == Kind.STUDY:
                # Ta'lim — faqat o'qish; javob qabul qilinmaydi.
                return Response({"error": "read_only"}, status=status.HTTP_409_CONFLICT)
            if not attempt.is_open:
                finish(attempt)
                return Response({"error": "finished", "result": result_of(attempt)}, status=status.HTTP_409_CONFLICT)
            item = get_object_or_404(AttemptItem, attempt=attempt, question_id=ser.validated_data["question"])
            if item.chosen_id is not None:
                return Response({"error": "already_answered"}, status=status.HTTP_409_CONFLICT)
            answer = get_object_or_404(Answer, pk=ser.validated_data["answer"], question_id=item.question_id)
            item.chosen = answer
            item.is_correct = answer.is_correct
            item.answered_at = timezone.now()
            item.save(update_fields=["chosen", "is_correct", "answered_at"])
            done = not attempt.items.filter(chosen__isnull=True).exists()
            if done and attempt.kind != Kind.STUDY:
                finish(attempt)
        q = item.question
        correct_id = q.answers.filter(is_correct=True).values_list("id", flat=True).first()
        return Response({
            "correct": answer.is_correct,
            "correct_answer": correct_id,
            "explanation": tri(q, "explanation"),
            "photo_hint": media_path("question", q, "photo_hint"),
            "audio_hint": media_path("question", q, "audio_hint"),
            "finished": attempt.finished_at is not None,
            "result": result_of(attempt) if attempt.finished_at else None,
        })


class FinishView(APIView):
    def post(self, request, pk):
        with transaction.atomic():
            attempt = get_object_or_404(Attempt.objects.select_for_update(), pk=pk, student=request.user)
            finish(attempt)
        return Response(serialize_attempt(attempt))


class HistoryView(APIView):
    def get(self, request):
        rows = Attempt.objects.filter(student=request.user, finished_at__isnull=False)[:30]
        return Response([
            {"id": a.id, "kind": a.kind, "ref": a.ref_id, "started_at": a.started_at.isoformat(), **result_of(a)}
            for a in rows
        ])

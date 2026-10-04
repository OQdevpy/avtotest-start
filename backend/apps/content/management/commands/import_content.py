"""content.json (Firebase eksportidan tayyorlangan) ni bazaga yuklaydi.

    python manage.py import_content --path ../frontend/public/content.json
    python manage.py import_content --path ... --flush   # avval eski kontentni o'chiradi

Rasm nomlari saqlanadi; rasm fayllari MEDIA_ROOT/question|category/ ichida bo'lishi
kerak (yoki demoda GitHub Pages media/ papkasida). Idempotent emas: --flush bilan
to'liq qayta yuklang.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.content.models import Answer, Category, Question, Stage, Variant, VariantQuestion


class Command(BaseCommand):
    help = "content.json dan bosqich, bo'lim, savol, javob va variantlarni yuklaydi"

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True)
        parser.add_argument("--flush", action="store_true", help="avval mavjud kontentni o'chiradi")

    @transaction.atomic
    def handle(self, *args, path, flush, **opts):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if flush:
            Variant.objects.all().delete()
            Stage.objects.all().delete()  # bo'lim, savol, javob kaskad bilan o'chadi

        stage_by = {}
        for s in data["stages"]:
            stage, _ = Stage.objects.update_or_create(
                number=s["number"],
                defaults=dict(title_uz=s["title"]["uz"], title_kr=s["title"]["kr"], title_ru=s["title"]["ru"]),
            )
            stage_by[s["id"]] = stage

        cat_by = {}
        for c in data["categories"]:
            cat = Category.objects.create(
                stage=stage_by[c["stage"]], order=c.get("order", 0),
                title_uz=c["title"]["uz"], title_kr=c["title"]["kr"], title_ru=c["title"]["ru"],
                icon=c.get("icon") or "",
            )
            cat_by[c["id"]] = cat

        q_by = {}
        for q in data["questions"]:
            question = Question.objects.create(
                category=cat_by[q["category"]], order=q.get("order", 0), is_published=True,
                text_uz=q["text"]["uz"], text_kr=q["text"]["kr"], text_ru=q["text"]["ru"],
                explanation_uz=q["explanation"]["uz"], explanation_kr=q["explanation"]["kr"],
                explanation_ru=q["explanation"]["ru"], image=q.get("image") or "",
            )
            q_by[q["id"]] = question
            Answer.objects.bulk_create(
                Answer(question=question, order=a.get("order", i),
                       text_uz=a["text"]["uz"], text_kr=a["text"]["kr"], text_ru=a["text"]["ru"],
                       is_correct=a["correct"])
                for i, a in enumerate(q["answers"])
            )

        for v in data.get("variants", []):
            stage = stage_by.get(v["stage"]) if v.get("stage") else None
            variant = Variant.objects.create(stage=stage, number=v["number"])
            VariantQuestion.objects.bulk_create(
                VariantQuestion(variant=variant, question=q_by[qid], order=i)
                for i, qid in enumerate(v["questions"]) if qid in q_by
            )

        self.stdout.write(self.style.SUCCESS(
            f"{Stage.objects.count()} bosqich, {Category.objects.count()} bo'lim, "
            f"{Question.objects.count()} savol, {Answer.objects.count()} javob, "
            f"{Variant.objects.count()} variant yuklandi."))

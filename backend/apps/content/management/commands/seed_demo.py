"""Demo kontent: 4 bosqich, bo'limlar, savollar va variantlar.

    python manage.py seed_demo            # bo'sh bazaga
    python manage.py seed_demo --force    # mavjud kontentni o'chirib qayta yaratadi
"""
import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.content.models import Answer, Category, Question, Stage, Variant, VariantQuestion

STAGES = {
    1: ("1-bosqich", "1-босқич", "1-й этап"),
    2: ("2-bosqich", "2-босқич", "2-й этап"),
    3: ("3-bosqich", "3-босқич", "3-й этап"),
    4: ("4-bosqich", "4-босқич", "4-й этап"),
}

CATEGORIES = {
    1: [("Ogohlantiruvchi belgilar", "Огоҳлантирувчи белгилар", "Предупреждающие знаки"),
        ("Imtiyoz belgilari", "Имтиёз белгилари", "Знаки приоритета"),
        ("Taqiqlovchi belgilar", "Тақиқловчи белгилар", "Запрещающие знаки")],
    2: [("Buyuruvchi belgilar", "Буюрувчи белгилар", "Предписывающие знаки"),
        ("Axborot-ishora belgilari", "Ахборот-ишора белгилари", "Информационно-указательные знаки"),
        ("Qo'shimcha axborot-ishora belgilari", "Қўшимча ахборот-ишора белгилари", "Знаки дополнительной информации")],
    3: [("Yo'l chiziqlari", "Йўл чизиқлари", "Дорожная разметка"),
        ("Avtomagistral", "Автомагистрал", "Автомагистраль")],
    4: [("Taniqlilik belgilari", "Таниқлилик белгилари", "Опознавательные знаки"),
        ("Birinchi tibbiy yordam", "Биринчи тиббий ёрдам", "Первая медицинская помощь")],
}

SAMPLES = [
    ("Qaysi belgi teng ahamiyatli yo'llar chorrahasiga yaqinlashib kelayotganlik haqida ogohlantiradi?",
     "Какой знак предупреждает о приближении к перекрёстку равнозначных дорог?",
     ["3", "5", "2", "1", "4"], 1),
    ("Qatnov qismining chetiga chizilgan sariq sidirg'a chiziqni bosishga ruxsat beriladimi?",
     "Разрешается ли наезжать на сплошную жёлтую линию у края проезжей части?",
     ["Ruxsat berilmaydi", "Ruxsat beriladi"], 0),
    ("Yo'l transport hodisasiga dahldor haydovchilar birinchi navbatda nima qilishlari kerak?",
     "Что в первую очередь должны сделать водители, причастные к ДТП?",
     ["Transport vositasini darhol to'xtatishi, avariya ishoralarini yoqishi va avariya sababli to'xtash "
      "belgisini o'rnatishi", "Yo'lning harakat qismini bo'shatishlari kerak",
      "Sodir etilgan hodisa xaqida YHXXga xabar berishi kerak"], 0),
    ("Chorrahada aylanma harakatlanish tashkil qilingan. Chorrahaga kirishda burilish uchun qaysi tasmani "
     "egallashingiz lozim?", "На перекрёстке с круговым движением какую полосу нужно занять для поворота?",
     ["O'ng yoki chap tasmani", "O'ng tasmani", "Chap tasmani"], 1),
    ("Qatnov qismi tomonidan yo'lovchilarning tushishi va chiqishiga qaysi hollarda ruxsat etiladi?",
     "В каких случаях разрешается посадка и высадка пассажиров со стороны проезжей части?",
     ["Haydovchining xohishiga ko'ra", "Transport vositasi majburiy to'xtaganda",
      "Trotuar tomondan iloji bo'lmasa, xavfsiz bo'lsa va boshqalarga halaqit bermasa"], 2),
    ("Qaysi belgi piyodalar o'tish joyini bildiradi?", "Какой знак обозначает пешеходный переход?",
     ["A", "V", "B"], 2),
]


class Command(BaseCommand):
    help = "Demo kontent yaratadi"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--per-category", type=int, default=12)

    @transaction.atomic
    def handle(self, *args, force, per_category, **opts):
        if Stage.objects.exists():
            if not force:
                raise CommandError("Kontent allaqachon bor. Qayta yaratish uchun --force.")
            Stage.objects.all().delete()
            Variant.objects.all().delete()

        rng = random.Random(42)
        all_q = {}
        for num, (uz, kr, ru) in STAGES.items():
            stage = Stage.objects.create(number=num, title_uz=uz, title_kr=kr, title_ru=ru)
            all_q[stage] = []
            for order, (tuz, tkr, tru) in enumerate(CATEGORIES[num]):
                cat = Category.objects.create(
                    stage=stage, title_uz=tuz, title_kr=tkr, title_ru=tru, order=order,
                    info_uz=f"«{tuz}» bo'limi bo'yicha qisqa ma'lumot. Rasmlarni admin paneldan yuklang.",
                    info_ru=f"Краткая информация по разделу «{tru}».",
                )
                for i in range(per_category):
                    text_uz, text_ru, answers, correct = SAMPLES[(i + order + num) % len(SAMPLES)]
                    q = Question.objects.create(
                        category=cat, order=i, text_uz=text_uz, text_ru=text_ru,
                        explanation_uz="To'g'ri javob yo'l harakati qoidalariga asoslangan.",
                    )
                    Answer.objects.bulk_create(
                        Answer(question=q, order=j, text_uz=t, is_correct=(j == correct))
                        for j, t in enumerate(answers)
                    )
                    all_q[stage].append(q)

        everything = [q for qs in all_q.values() for q in qs]
        for n in range(1, 61):
            self._variant(None, n, rng.sample(everything, min(20, len(everything))))
        for stage, qs in all_q.items():
            for n in range(1, 19):
                self._variant(stage, n, rng.sample(qs, min(20, len(qs))))
        self.stdout.write(self.style.SUCCESS(
            f"{Stage.objects.count()} bosqich, {Category.objects.count()} bo'lim, "
            f"{Question.objects.count()} savol, {Variant.objects.count()} variant yaratildi."))

    def _variant(self, stage, number, questions):
        v = Variant.objects.create(stage=stage, number=number)
        VariantQuestion.objects.bulk_create(
            VariantQuestion(variant=v, question=q, order=i) for i, q in enumerate(questions))

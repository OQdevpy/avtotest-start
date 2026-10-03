from django.core.management.base import BaseCommand

from apps.accounts.models import Student, generate_code


class Command(BaseCommand):
    help = "O'quvchi yaratadi va bir martalik ko'rsatiladigan kirish kodini chiqaradi."

    def add_arguments(self, parser):
        parser.add_argument("full_name")
        parser.add_argument("--phone", default="")
        parser.add_argument("--devices", type=int, default=1)

    def handle(self, *args, full_name, phone, devices, **opts):
        code = generate_code()
        s = Student(full_name=full_name, phone=phone, max_devices=devices)
        s.set_code(code)
        s.save()
        self.stdout.write(self.style.SUCCESS(f"{s.full_name}: kirish kodi {code}"))

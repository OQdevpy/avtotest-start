import os

os.environ["DEBUG"] = "1"
os.environ.pop("DB_NAME", None)
os.environ.pop("REDIS_URL", None)

from .settings import *  # noqa: E402,F401,F403

ALLOWED_HOSTS = ["testserver"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

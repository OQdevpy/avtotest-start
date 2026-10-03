from .models import LANGS


def tri(obj, prefix):
    """Uchala tildagi matn: {"uz": ..., "kr": ..., "ru": ...}. Mijoz til
    almashtirganda serverga qayta murojaat qilmaydi."""
    return {lang: obj.tr(prefix, lang) for lang in LANGS}


def media_path(kind, obj, field):
    return f"{kind}/{obj.pk}/{field}" if getattr(obj, field) else None
